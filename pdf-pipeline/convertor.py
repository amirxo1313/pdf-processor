#!/usr/bin/env python3
import os
import subprocess
import glob
import shutil
import sys
import logging
from pathlib import Path

# === CONFIG ===
INPUT_DIR = "/data/pdfs"
OUTPUT_DIR = "/data/output"
DPI = 300
DEVICE = "png16m"
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run_cmd(cmd, desc):
    logging.info(f"[{desc}] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"[{desc}] SUCCESS")
    else:
        logging.warning(f"[{desc}] FAILED (code {result.returncode})\nSTDERR: {result.stderr.strip()}")
    return result

def extract_with_ghostscript(pdf_path, out_dir):
    cmd = [
        "gs", "-dNOPAUSE", "-dBATCH", "-dSAFER",
        f"-sDEVICE={DEVICE}", f"-r{DPI}",
        f"-sOutputFile={out_dir}/page-%03d.png",
        pdf_path
    ]
    return run_cmd(cmd, "Ghostscript")

def extract_with_magick(pdf_path, out_dir):
    cmd = ["convert", "-density", str(DPI), pdf_path, f"{out_dir}/page-%03d.png"]
    return run_cmd(cmd, "ImageMagick")

def extract_with_tesseract_fallback(pdf_path, out_dir):
    temp_pdf = f"/tmp/{Path(pdf_path).stem}_tess.pdf"
    cmd1 = ["tesseract", pdf_path, temp_pdf.replace(".pdf", ""), "-l", "fas+eng", "pdf"]
    result1 = run_cmd(cmd1, "Tesseract PDF Render")
    if result1.returncode != 0:
        return result1

    # Extract images from Tesseract-generated PDF
    cmd2 = [
        "pdftoppm", "-png", "-r", str(DPI),
        temp_pdf, f"{out_dir}/page"
    ]
    result2 = run_cmd(cmd2, "pdftoppm (Tesseract output)")
    try:
        os.remove(temp_pdf)
    except:
        pass
    return result2

def safe_makedirs(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")

# === MAIN LOOP ===
def main():
    pdf_files = glob.glob(f"{INPUT_DIR}/*.pdf")
    if not pdf_files:
        logging.error(f"No PDFs found in {INPUT_DIR}")
        return

    for pdf in sorted(pdf_files):
        basename = Path(pdf).stem
        out_dir = f"{OUTPUT_DIR}/{basename}"
        safe_makedirs(out_dir)
        logging.info(f"Processing: {pdf} → {out_dir}")

        success = False

        # Clean output directory if it exists
        if os.path.exists(out_dir):
            for f in os.listdir(out_dir):
                if f.endswith(".png"):
                    os.remove(os.path.join(out_dir, f))

        # Layer 1: Ghostscript
        if not success:
            result = extract_with_ghostscript(pdf, out_dir)
            if result.returncode == 0 and any(f.endswith(".png") for f in os.listdir(out_dir)):
                success = True
                logging.info(f"Ghostscript extracted pages successfully.")

        # Layer 2: ImageMagick
        if not success:
            result = extract_with_magick(pdf, out_dir)
            if result.returncode == 0 and any(f.endswith(".png") for f in os.listdir(out_dir)):
                success = True
                logging.info(f"ImageMagick extracted pages successfully.")

        # Layer 3: Tesseract + pdftoppm
        if not success:
            result = extract_with_tesseract_fallback(pdf, out_dir)
            if result.returncode == 0 and any(f.endswith(".png") for f in os.listdir(out_dir)):
                success = True
                logging.warning(f"Tesseract fallback succeeded (OCR render path).")
            else:
                logging.error(f"ALL METHODS FAILED for {pdf}")

        if success:
            logging.info(f"COMPLETED: {pdf}\n")
        else:
            logging.error(f"FINAL FAILURE: {pdf}\n")

if __name__ == "__main__":
    main()
