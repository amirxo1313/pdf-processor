#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian Legal PDF → ParsBERT JSON Converter (No OCR)

- Recursively scans an input directory for PDF files
- Classifies PDFs as text-based vs image-based (no OCR used)
- Extracts text from text-based PDFs using PyMuPDF/pdfminer
- Normalizes Persian characters and cleans common footer/header noise
- Emits JSON per file with schema required for ParsBERT:
  {
    "title": str,
    "paragraphs": List[str],
    "metadata": {
      "source_path": str,
      "page_count": int,
      "text_type": "text" | "image",
      "language": "fa",
      "integrity_score": float
    }
  }
- Writes a conversion report and a failed-files log

Notes:
- No OCR is performed. Image-based PDFs are logged as failed.
- UTF-8 output with ensure_ascii=False.
"""

from __future__ import annotations

import json
import os
import re
import time
import hashlib
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# Dependencies: PyMuPDF (fitz) and pdfminer.six are expected to be available
import fitz  # type: ignore  # PyMuPDF
from pdfminer.high_level import extract_text_to_fp  # type: ignore
from pdfminer.layout import LAParams  # type: ignore
import io


# ------------------------------- Configuration -------------------------------

DEFAULT_INPUT_DIR = "/home/amirxo/Desktop/New Folder 2"
DEFAULT_OUTPUT_DIR = "/home/amirxo/Desktop/ParsBERT_training_dataset"
DEFAULT_FAILED_LOG = "/home/amirxo/Desktop/New Folder 2/failed_files.log"
DEFAULT_REPORT_FILE = "/home/amirxo/Desktop/ParsBERT_training_dataset/conversion_report.log"


# --------------------------------- Models -----------------------------------

@dataclass
class ConversionStats:
    total_files: int = 0
    processed: int = 0
    success: int = 0
    failed: int = 0
    text_pdfs: int = 0
    image_pdfs: int = 0
    total_time_s: float = 0.0


# ------------------------------- Utils: Text ---------------------------------

PERSIAN_CHAR_MAP: Dict[str, str] = {
    "ك": "ک",  # Arabic Kaf → Persian Kaf
    "ي": "ی",  # Arabic Yeh → Persian Yeh
    "ى": "ی",  # Alef Maksura → Persian Yeh
    "ة": "ه",  # Teh Marbuta → Heh
    "٠": "۰", "١": "۱", "٢": "۲", "٣": "۳", "٤": "۴",
    "٥": "۵", "٦": "۶", "٧": "۷", "٨": "۸", "٩": "۹",
}


def normalize_persian_text(text: str) -> str:
    """Normalize Persian text for consistency and cleanliness.

    - Map Arabic variants to Persian equivalents
    - Normalize Unicode (NFC)
    - Collapse excessive whitespace
    - Remove control characters
    """
    if not text:
        return ""

    for ar, fa in PERSIAN_CHAR_MAP.items():
        text = text.replace(ar, fa)

    # Remove control chars
    text = "".join(ch for ch in text if not unicodedata.category(ch).startswith("C"))

    # Normalize Unicode
    text = unicodedata.normalize("NFC", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_header_footer_noise(page_texts: List[str]) -> List[str]:
    """Heuristically remove repeated header/footer lines across pages.

    Approach: find lines appearing in the majority of pages at first/last line
    positions and drop them.
    """
    if not page_texts:
        return page_texts

    first_lines: Dict[str, int] = {}
    last_lines: Dict[str, int] = {}

    for txt in page_texts:
        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        if not lines:
            continue
        first_lines[lines[0]] = first_lines.get(lines[0], 0) + 1
        last_lines[lines[-1]] = last_lines.get(lines[-1], 0) + 1

    threshold = max(2, int(0.5 * len(page_texts)))  # repeated in ≥50% pages

    common_first = {l for l, c in first_lines.items() if c >= threshold}
    common_last = {l for l, c in last_lines.items() if c >= threshold}

    cleaned_pages: List[str] = []
    for txt in page_texts:
        lines = list(txt.split("\n"))
        if lines and lines[0].strip() in common_first:
            lines = lines[1:]
        if lines and lines[-1].strip() in common_last:
            lines = lines[:-1]
        cleaned_pages.append("\n".join(lines))

    return cleaned_pages


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs suitable for ParsBERT input.

    - Prefer double-newline or long-line boundaries
    - Keep paragraphs reasonably sized; merge short fragments
    """
    if not text:
        return []

    # Recover some paragraph structure from single newlines by splitting on
    # blank lines first, then fallback to long lines.
    blocks = re.split(r"\n\s*\n", text)
    paragraphs: List[str] = []

    buffer: List[str] = []
    current_len = 0
    MAX_LEN = 1200

    for block in blocks:
        cleaned = block.strip()
        if not cleaned:
            continue
        if current_len + len(cleaned) <= MAX_LEN:
            buffer.append(cleaned)
            current_len += len(cleaned)
        else:
            if buffer:
                paragraphs.append("\n".join(buffer).strip())
            buffer = [cleaned]
            current_len = len(cleaned)

    if buffer:
        paragraphs.append("\n".join(buffer).strip())

    return paragraphs


def estimate_integrity_score(text: str) -> float:
    """Estimate an integrity/quality score in [0,1] for extracted Persian text.

    Components:
    - Persian character ratio
    - Presence of Persian punctuation
    - Reasonable average line length
    """
    if not text:
        return 0.0

    total_chars = len(text)
    persian_chars = len(re.findall(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]", text))
    ratio = persian_chars / total_chars if total_chars else 0.0

    persian_punct = len(re.findall(r"[،؛؟]", text))
    punct_score = min(1.0, persian_punct / 100.0)

    lines = [l for l in text.split("\n") if l.strip()]
    if lines:
        reasonable = sum(1 for l in lines if len(l) >= 10)
        line_score = reasonable / len(lines)
    else:
        line_score = 0.0

    # Simple average
    score = (ratio + punct_score + line_score) / 3.0
    return round(max(0.0, min(1.0, score)), 4)


# ----------------------------- PDF Classification ----------------------------

def classify_pdf_textuality(pdf_path: Path) -> Tuple[str, float]:
    """Classify a PDF as 'text' or 'image' using text density metrics.

    Returns (text_type, confidence)
    """
    try:
        # Extract rough text using pdfminer (fast-ish, layout-agnostic)
        buf = io.StringIO()
        with open(pdf_path, "rb") as f:
            extract_text_to_fp(f, buf, laparams=LAParams())
        txt = buf.getvalue()

        file_size = pdf_path.stat().st_size
        text_len = len(txt.strip())
        density = (text_len / file_size) if file_size else 0.0

        # Heuristics
        if text_len >= 200 and density >= 0.2:
            conf = min(1.0, text_len / 4000.0)
            return "text", conf
        return "image", max(0.0, min(1.0, 1.0 - density))
    except Exception:
        return "image", 0.5


# ----------------------------- PDF Text Extraction ---------------------------

def extract_text_pymupdf(pdf_path: Path) -> Tuple[str, int, List[str]]:
    """Extract text per page using PyMuPDF; return full_text, page_count, page_texts."""
    doc = fitz.open(str(pdf_path))
    pages: List[str] = []
    for page in doc:
        try:
            t = page.get_text() or ""
        except Exception:
            t = ""
        pages.append(t)
    page_count = len(doc)
    doc.close()
    return "\n\n".join(pages), page_count, pages


def extract_text_pdfminer(pdf_path: Path) -> str:
    """Extract text using pdfminer with tuned layout params."""
    try:
        output = io.StringIO()
        with open(pdf_path, "rb") as f:
            laparams = LAParams(line_overlap=0.5, char_margin=2.0, word_margin=0.1, boxes_flow=0.5)
            extract_text_to_fp(f, output, laparams=laparams)
        return output.getvalue()
    except Exception:
        return ""


def extract_text_hybrid(pdf_path: Path) -> Tuple[str, int, List[str]]:
    """Hybrid: PyMuPDF first; if weak, fallback to pdfminer; return with page_texts."""
    pymu_text, page_count, pages = extract_text_pymupdf(pdf_path)
    if len(pymu_text.strip()) >= 100:
        return pymu_text, page_count, pages
    pm_text = extract_text_pdfminer(pdf_path)
    if len(pm_text) > len(pymu_text):
        # pdfminer lacks page splits; reuse page_count from PyMuPDF
        return pm_text, page_count, pages
    return pymu_text, page_count, pages


# -------------------------------- Main Runner --------------------------------

def compute_output_filename(pdf_path: Path) -> str:
    """Create a collision-resistant output filename using stem+hash."""
    h = hashlib.sha256(str(pdf_path).encode("utf-8")).hexdigest()[:12]
    return f"{pdf_path.stem}_{h}.json"


def convert_single_pdf(pdf_path: Path) -> Tuple[Optional[dict], Optional[dict]]:
    """Convert a single PDF to ParsBERT-ready JSON.

    Returns (json_doc, failure_record). Only one of them will be non-None.
    """
    text_type, _ = classify_pdf_textuality(pdf_path)
    if text_type == "image":
        return None, {"path": str(pdf_path), "reason": "image_based_pdf_no_ocr"}

    full_text, page_count, page_texts = extract_text_hybrid(pdf_path)
    if not full_text or len(full_text.strip()) < 50:
        return None, {"path": str(pdf_path), "reason": "insufficient_text"}

    # Clean per-page noise then normalize
    cleaned_pages = remove_header_footer_noise(page_texts)
    cleaned_full = "\n\n".join(cleaned_pages)
    normalized = normalize_persian_text(cleaned_full)

    # Title heuristic: PDF metadata title or first non-trivial line
    title = None
    try:
        doc = fitz.open(str(pdf_path))
        meta = doc.metadata or {}
        if meta.get("title") and len(str(meta["title"]).strip()) >= 3:
            title = str(meta["title"]).strip()
        doc.close()
    except Exception:
        pass
    if not title:
        first_line = next((ln.strip() for ln in normalized.split("\n") if len(ln.strip()) >= 6), "")
        title = first_line if first_line else pdf_path.stem

    paragraphs = split_into_paragraphs(normalized)
    integrity_score = estimate_integrity_score(normalized)

    doc_json = {
        "title": title,
        "paragraphs": paragraphs,
        "metadata": {
            "source_path": str(pdf_path),
            "page_count": page_count,
            "text_type": "text",
            "language": "fa",
            "integrity_score": integrity_score,
        },
    }

    return doc_json, None


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def convert_directory(
    input_dir: str = DEFAULT_INPUT_DIR,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    failed_log: str = DEFAULT_FAILED_LOG,
    report_file: str = DEFAULT_REPORT_FILE,
) -> None:
    """Run the conversion pipeline over a directory tree."""
    t0 = time.time()
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)

    ensure_dir(out_dir)
    out_dir.chmod(0o755)

    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")

    pdf_files = list(in_dir.rglob("*.pdf"))
    stats = ConversionStats(total_files=len(pdf_files))
    failures: List[dict] = []

    for _, pdf_path in enumerate(pdf_files, 1):
        # Convert
        doc_json, fail = convert_single_pdf(pdf_path)
        stats.processed += 1

        if doc_json is None:
            stats.failed += 1
            if fail:
                if fail.get("reason") == "image_based_pdf_no_ocr":
                    stats.image_pdfs += 1
                failures.append(fail)
            continue

        stats.success += 1
        stats.text_pdfs += 1
        out_name = compute_output_filename(pdf_path)
        out_path = out_dir / out_name
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc_json, f, ensure_ascii=False, indent=2)

    stats.total_time_s = time.time() - t0

    # Write failed log (JSON lines)
    if failures:
        with open(failed_log, "w", encoding="utf-8") as f:
            for rec in failures:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Write report
    success_rate = (stats.success / stats.total_files * 100.0) if stats.total_files else 0.0
    report_lines = [
        "=" * 70,
        "ParsBERT Conversion Report (No OCR)",
        "=" * 70,
        f"Input Dir: {in_dir}",
        f"Output Dir: {out_dir}",
        f"Failed Log: {failed_log}",
        "",
        f"Total PDFs: {stats.total_files}",
        f"Processed: {stats.processed}",
        f"Success: {stats.success}",
        f"Failed: {stats.failed}",
        f"Text PDFs: {stats.text_pdfs}",
        f"Image PDFs (skipped): {stats.image_pdfs}",
        f"Success Rate: {success_rate:.2f}%",
        f"Total Time: {stats.total_time_s:.2f}s",
        "=" * 70,
    ]

    ensure_dir(Path(report_file).parent)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


def main() -> None:
    convert_directory(
        input_dir=DEFAULT_INPUT_DIR,
        output_dir=DEFAULT_OUTPUT_DIR,
        failed_log=DEFAULT_FAILED_LOG,
        report_file=DEFAULT_REPORT_FILE,
    )


if __name__ == "__main__":
    main()


