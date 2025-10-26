#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to JSON Converter - Robust Version
استفاده از چند کتابخانه به صورت fallback برای استخراج بهتر متن
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

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
            except:
                continue

        return text, page_count
    except Exception as e:
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
                except:
                    continue

        return text, page_count
    except Exception as e:
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
    # Source directory
    source_dir = "/home/amirxo/Desktop/New Folder 2"

    # Output JSON file
    output_file = "/home/amirxo/git/pdf_training_data.json"

    print("="*70)
    print("🔄 PDF to JSON Converter - Robust Version")
    print("="*70)
    print(f"📂 Source: {source_dir}")
    print(f"📄 Output: {output_file}")
    print("="*70)
    print()

    convert_pdfs_to_json(source_dir, output_file)

