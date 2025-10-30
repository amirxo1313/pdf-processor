#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to JSON Converter - Robust Version
استفاده از چند کتابخانه به صورت fallback برای استخراج بهتر متن
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Optional deps for OCR
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except Exception:
    HAS_PYMUPDF = False

try:
    from PIL import Image
    import pytesseract
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False

# Try multiple PDF libraries
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

def extract_text_pypdf(pdf_path):
    """Extract text using PyPDF"""
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        page_count = len(reader.pages)

        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception:
                continue

        return text, page_count
    except Exception:
        return None, 0

def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber - better for Persian"""
    try:
        text = ""
        page_count = 0

        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception:
                    continue

        return text, page_count
    except Exception:
        return None, 0

def extract_text_robust(pdf_path):
    """Extract text using multiple methods as fallback"""
    text = None
    page_count = 0

    # Try pdfplumber first (best for Persian/Farsi)
    if HAS_PDFPLUMBER:
        text, page_count = extract_text_pdfplumber(pdf_path)

    # Fallback to pypdf if pdfplumber failed or returns empty text
    if not text or len(text.strip()) < 100:
        if HAS_PYPDF:
            text, page_count = extract_text_pypdf(pdf_path)

    if text and len(text.strip()) >= 50:
        return text.strip(), page_count
    else:
        return None, 0

def _extract_text_pdfplumber_per_page(pdf_path: Path) -> Tuple[List[str], int]:
    pages_text: List[str] = []
    page_count: int = 0
    if not HAS_PDFPLUMBER:
        return pages_text, page_count
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""
                pages_text.append(page_text)
    except Exception:
        return [], 0
    return pages_text, page_count

def _extract_text_pypdf_per_page(pdf_path: Path) -> Tuple[List[str], int]:
    pages_text: List[str] = []
    page_count: int = 0
    if not HAS_PYPDF:
        return pages_text, page_count
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        page_count = len(reader.pages)
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            pages_text.append(page_text)
    except Exception:
        return [], 0
    return pages_text, page_count

def extract_text_native_per_page(pdf_path: Path) -> Tuple[List[str], int]:
    pages_text, page_count = _extract_text_pdfplumber_per_page(pdf_path)
    if not pages_text or sum(len(t.strip()) for t in pages_text) < 50:
        alt_pages_text, alt_count = _extract_text_pypdf_per_page(pdf_path)
        if sum(len(t.strip()) for t in alt_pages_text) > sum(len(t.strip()) for t in pages_text):
            pages_text, page_count = alt_pages_text, alt_count
    return pages_text, page_count

def extract_text_ocr_per_page(pdf_path: Path) -> Tuple[List[str], int, Optional[float]]:
    """OCR each page using PyMuPDF rendering + pytesseract. Returns (texts, page_count, avg_confidence)."""
    if not (HAS_PYMUPDF and HAS_TESSERACT):
        return [], 0, None
    doc = None
    try:
        doc = fitz.open(str(pdf_path))
        page_count = doc.page_count
        ocr_texts: List[str] = []
        confidences: List[float] = []
        # Use moderate DPI to balance quality and speed
        zoom = 2.0  # ~144 DPI if default is 72
        mat = fitz.Matrix(zoom, zoom)
        for i in range(page_count):
            try:
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                # Try Farsi traineddata first
                try:
                    text = pytesseract.image_to_string(image, lang="fas")
                    tsv = pytesseract.image_to_data(image, lang="fas", output_type=pytesseract.Output.DATAFRAME)  # type: ignore
                except Exception:
                    text = pytesseract.image_to_string(image)
                    tsv = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)  # type: ignore
                ocr_texts.append(text or "")
                try:
                    # Filter valid confidences (non -1)
                    conf_series = tsv["conf"]
                    valid = [float(c) for c in conf_series if str(c) not in ("-1", "nan")]
                    if valid:
                        confidences.append(sum(valid) / len(valid))
                except Exception:
                    pass
            except Exception:
                ocr_texts.append("")
        avg_conf = (sum(confidences) / len(confidences)) / 100.0 if confidences else None
        return ocr_texts, page_count, avg_conf
    except Exception:
        return [], 0, None
    finally:
        try:
            if doc is not None:
                doc.close()
        except Exception:
            pass

def enumerate_pdfs_recursive(input_directory: Path) -> List[Path]:
    return [p for p in input_directory.rglob("*.pdf") if p.is_file()]

def classify_pdf_text_vs_image(pdf_path: Path) -> str:
    """Classify PDF as 'text' or 'image' by attempting native text extraction."""
    pages_text, page_count = extract_text_native_per_page(pdf_path)
    total_text_len = sum(len(t.strip()) for t in pages_text)
    if page_count == 0:
        return "image"
    avg_len = total_text_len / max(1, page_count)
    # Heuristic: short or empty text suggests scanned/image-based
    return "text" if avg_len >= 80 else "image"

_ARABIC_TO_PERSIAN = str.maketrans({
    "ك": "ک",
    "ي": "ی",
})
_ARABIC_INDIC_TO_PERSIAN_DIGITS = str.maketrans({
    "0": "۰", "1": "۱", "2": "۲", "3": "۳", "4": "۴",
    "5": "۵", "6": "۶", "7": "۷", "8": "۸", "9": "۹",
    "٠": "۰", "١": "۱", "٢": "۲", "٣": "۳", "٤": "۴",
    "٥": "۵", "٦": "۶", "٧": "۷", "٨": "۸", "٩": "۹",
})

def normalize_persian_text(text: str) -> str:
    """Normalize Persian typography: characters, digits, and spaces."""
    if not text:
        return ""
    text = text.translate(_ARABIC_TO_PERSIAN)
    text = text.translate(_ARABIC_INDIC_TO_PERSIAN_DIGITS)
    # Replace ZWNJ and other invisibles with space
    text = text.replace("\u200c", " ").replace("\u200f", " ")
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    # Restore paragraph breaks from original double newlines if present markers survived
    text = text.replace(" \n ", "\n").replace("\n ", "\n").replace(" \n", "\n")
    text = re.sub(r"(\n\s*){2,}", "\n\n", text)
    return text.strip()

def remove_repeated_headers_footers(pages_text: List[str]) -> List[str]:
    """Remove lines repeated across many pages (likely headers/footers)."""
    if not pages_text:
        return pages_text
    page_lines: List[List[str]] = []
    freq: Dict[str, int] = {}
    for t in pages_text:
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        page_lines.append(lines)
        uniq = set(lines)
        for ln in uniq:
            if 0 < len(ln) <= 200:
                freq[ln] = freq.get(ln, 0) + 1
    threshold = max(2, int(0.5 * len(pages_text)))
    repeated = {ln for ln, c in freq.items() if c >= threshold}
    cleaned: List[str] = []
    for lines in page_lines:
        kept = [ln for ln in lines if ln not in repeated]
        cleaned.append("\n".join(kept))
    return cleaned

def split_into_paragraphs(text: str, max_len: int = 1200) -> List[str]:
    if not text:
        return []
    # First split by logical breaks
    blocks = [b.strip() for b in re.split(r"\n\s*\n|\r\n\r\n", text) if b.strip()]
    sentences = []
    for blk in blocks:
        # Further split by Persian sentence punctuation
        parts = re.split(r"([\.\!\؟\!\;\؛])", blk)
        # Re-join punctuation tokens
        cur = ""
        for i in range(0, len(parts), 2):
            seg = parts[i].strip()
            punc = parts[i+1] if i+1 < len(parts) else ""
            if not seg:
                continue
            s = (seg + (punc or "")).strip()
            sentences.append(s)
    # Pack into paragraphs
    paragraphs: List[str] = []
    buf = []
    cur_len = 0
    for s in sentences:
        s2 = s if s.endswith("\n") else s + " "
        if cur_len + len(s2) > max_len and buf:
            paragraphs.append("".join(buf).strip())
            buf = [s2]
            cur_len = len(s2)
        else:
            buf.append(s2)
            cur_len += len(s2)
    if buf:
        paragraphs.append("".join(buf).strip())
    # Fallback: if no sentences detected use block splitting
    if not paragraphs:
        paragraphs = blocks
    return [p for p in paragraphs if p]

def compute_integrity_score(text_type: str, page_count: int, total_chars: int, avg_ocr_conf: Optional[float], empty_page_ratio: float) -> float:
    # Character coverage proxy
    char_ratio = min(1.0, total_chars / float(max(1, page_count) * 400))
    if text_type == "text":
        base = 0.90
        penalty = 0.20 * empty_page_ratio
        score = base * (0.6 * char_ratio + 0.4) - penalty
    else:
        base = 0.80
        conf = avg_ocr_conf if avg_ocr_conf is not None else 0.75
        score = base * (0.5 * char_ratio + 0.5 * conf)
    return max(0.0, min(1.0, score))

def build_output_json(pdf_path: Path, title: str, paragraphs: List[str], page_count: int, text_type: str, integrity_score: float) -> Dict[str, object]:
    return {
        "title": title,
        "paragraphs": paragraphs,
        "metadata": {
            "source_path": str(pdf_path),
            "page_count": page_count,
            "text_type": text_type,
            "language": "fa",
            "integrity_score": float(f"{integrity_score:.4f}")
        }
    }

def validate_output_schema(doc: Dict[str, object]) -> Tuple[bool, str]:
    try:
        if not isinstance(doc.get("title"), str):
            return False, "title must be string"
        paras = doc.get("paragraphs")
        if not isinstance(paras, list) or not all(isinstance(p, str) for p in paras):
            return False, "paragraphs must be list of strings"
        meta = doc.get("metadata")
        if not isinstance(meta, dict):
            return False, "metadata missing"
        required = ["source_path", "page_count", "text_type", "language", "integrity_score"]
        for k in required:
            if k not in meta:
                return False, f"metadata.{k} missing"
        if meta.get("language") != "fa":
            return False, "language must be fa"
        if not isinstance(meta.get("page_count"), int):
            return False, "page_count must be int"
        if not isinstance(meta.get("integrity_score"), float):
            return False, "integrity_score must be float"
        if meta.get("text_type") not in ("text", "image"):
            return False, "text_type invalid"
        return True, "ok"
    except Exception as e:
        return False, f"exception: {e}"

def process_legal_pdfs_to_parsbert(
    input_directory: Path,
    output_directory: Path,
    report_log: Path,
    failed_log: Path,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    report_log.parent.mkdir(parents=True, exist_ok=True)
    failed_log.parent.mkdir(parents=True, exist_ok=True)

    pdf_paths = enumerate_pdfs_recursive(input_directory)
    total = len(pdf_paths)
    success = 0
    failures = 0
    with open(report_log, "a", encoding="utf-8") as rep, open(failed_log, "a", encoding="utf-8") as bad:
        rep.write(f"=== Conversion started at {datetime.now().isoformat()} ===\n")
        rep.write(f"Input: {input_directory}\nOutput: {output_directory}\nCount: {total}\n\n")
        for idx, pdf_path in enumerate(pdf_paths, 1):
            try:
                text_type = classify_pdf_text_vs_image(pdf_path)
                if text_type == "text":
                    pages_text, page_count = extract_text_native_per_page(pdf_path)
                    avg_conf = None
                else:
                    pages_text, page_count, avg_conf = extract_text_ocr_per_page(pdf_path)
                # Basic empty-page metric
                empty_pages = sum(1 for t in pages_text if len((t or "").strip()) == 0)
                empty_ratio = empty_pages / float(max(1, len(pages_text)))
                # Normalize and clean
                pages_text = [normalize_persian_text(t) for t in pages_text]
                pages_text = remove_repeated_headers_footers(pages_text)
                # Structure to paragraphs
                normalized_full = "\n\n".join(pages_text)
                paragraphs = split_into_paragraphs(normalized_full, max_len=1200)
                total_chars = sum(len(p) for p in paragraphs)
                integrity = compute_integrity_score(text_type, page_count, total_chars, avg_conf if text_type == "image" else None, empty_ratio)
                title = pdf_path.stem
                data = build_output_json(pdf_path, title, paragraphs, page_count, text_type, integrity)
                # Write JSON file per PDF
                out_file = output_directory / f"{pdf_path.stem}.json"
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                # Validation stage
                ok, reason = validate_output_schema(data)
                if not ok or integrity < 0.85:
                    bad.write(f"{str(pdf_path)}\t{reason if not ok else 'low_integrity'}\t{integrity:.4f}\n")
                rep.write(
                    f"[{idx}/{total}] OK {pdf_path.name} | type={text_type} pages={page_count} integrity={integrity:.3f} -> {out_file}\n"
                )
                success += 1
            except Exception as e:
                rep.write(f"[{idx}/{total}] FAIL {pdf_path.name}: {e}\n")
                bad.write(f"{str(pdf_path)}\t{e}\n")
                failures += 1
        rep.write(f"\nSummary: success={success} failures={failures} rate={(success/total if total else 0):.2%}\n")
        rep.write(f"=== Conversion finished at {datetime.now().isoformat()} ===\n\n")

def is_persian_text(text):
    """Check if text contains Persian/Farsi characters"""
    if not text:
        return False

    persian_range = set(range(0x0600, 0x06FF))
    text_chars = set(ord(c) for c in text[:500])
    persian_count = len(text_chars.intersection(persian_range))

    return persian_count > len(text_chars) * 0.1

def convert_pdfs_to_json(directory_path, output_json_path):
    """Convert all PDF files in directory to JSON"""

    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ Directory not found: {directory_path}")
        return

    # Find all PDF files
    pdf_files = list(directory.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {directory_path}")
        return

    print(f"📁 Found {len(pdf_files)} PDF files")
    print(f"📚 Libraries available:")
    print(f"  - pdfplumber: {'✓' if HAS_PDFPLUMBER else '✗'}")
    print(f"  - pypdf: {'✓' if HAS_PYPDF else '✗'}")
    print()

    # Process all PDFs
    converted_data = []
    successful = 0
    failed = 0

    for idx, pdf_file in enumerate(pdf_files, 1):
        # Print progress every 100 files or first 10
        if idx % 100 == 0 or idx <= 10:
            print(f"⏳ Processing [{idx:,}/{len(pdf_files):,}]")

        try:
            text, page_count = extract_text_robust(pdf_file)

            if text:
                # Detect language
                language = "persian" if is_persian_text(text) else "mixed"

                # Create document entry
                doc = {
                    "id": f"doc_{idx}",
                    "filename": pdf_file.name,
                    "text": text,
                    "metadata": {
                        "page_count": page_count,
                        "language": language,
                        "source_path": str(pdf_file),
                        "processed_at": datetime.now().isoformat(),
                        "word_count": len(text.split()),
                        "character_count": len(text)
                    }
                }

                converted_data.append(doc)
                successful += 1
            else:
                failed += 1

        except Exception as e:
            failed += 1
            continue

    # Write to JSON file
    output_path = Path(output_json_path)

    print(f"\n💾 Saving to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)

    # Statistics
    total_chars = sum(len(doc['text']) for doc in converted_data)
    total_words = sum(doc['metadata']['word_count'] for doc in converted_data)

    print("\n" + "="*70)
    print("✅ Processing Complete!")
    print("="*70)
    print(f"✓ Successfully converted: {successful:,} files ({successful*100//len(pdf_files)}%)")
    print(f"✗ Failed to convert: {failed:,} files ({failed*100//len(pdf_files)}%)")
    print(f"✓ Total characters extracted: {total_chars:,}")
    print(f"✓ Total words extracted: {total_words:,}")
    print(f"✓ Output file: {output_path}")
    print(f"✓ File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print("="*70)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Legal PDF → ParsBERT JSON Conversion")
    parser.add_argument("--input", dest="input_dir", default="/home/amirxo/Desktop/New Folder 2/", help="Input directory (recursive)")
    parser.add_argument("--output", dest="output_dir", default="/home/amirxo/Desktop/New Folder 3/", help="Output directory for JSON files")
    parser.add_argument("--report", dest="report_log", default="/home/amirxo/Desktop/New Folder 3/conversion_report.log", help="Conversion report log path")
    parser.add_argument("--failed", dest="failed_log", default="/home/amirxo/Desktop/New Folder 3/failed_files.log", help="Failed files log path")
    parser.add_argument("--legacy-batch", action="store_true", help="Run legacy single-JSON batch mode instead")
    parser.add_argument("--legacy-output", default="/home/amirxo/git/pdf_training_data.json", help="Legacy batch output JSON path")

    args = parser.parse_args()

    if args.legacy_batch:
        print("="*70)
        print("🔄 PDF to JSON Converter - Legacy Batch Mode")
        print("="*70)
        print(f"📂 Source: {args.input_dir}")
        print(f"📄 Output: {args.legacy_output}")
        print("="*70)
        print()
        convert_pdfs_to_json(args.input_dir, args.legacy_output)
        sys.exit(0)

    print("="*70)
    print("⚖️  Legal PDF → ParsBERT JSON Conversion")
    print("="*70)
    print(f"📂 Input:  {args.input_dir}")
    print(f"📁 Output: {args.output_dir}")
    print(f"📝 Report: {args.report_log}")
    print(f"🧾 Failed: {args.failed_log}")
    print("="*70)
    print()

    process_legal_pdfs_to_parsbert(
        input_directory=Path(args.input_dir),
        output_directory=Path(args.output_dir),
        report_log=Path(args.report_log),
        failed_log=Path(args.failed_log),
    )

