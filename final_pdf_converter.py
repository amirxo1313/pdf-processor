#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تبدیل PDF به JSON - نسخه نهایی
با مدیریت خطا و رد کردن فایل‌های خراب
"""

import json
import sys
from pathlib import Path
from datetime import datetime

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

def extract_text_robust(pdf_path):
    """استخراج متن با fallback"""
    text = None
    page_count = 0

    # روش 1: pdfplumber (بهترین برای فارسی)
    if HAS_PDFPLUMBER:
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except:
                        continue
        except:
            pass

    # روش 2: pypdf (fallback)
    if (not text or len(text.strip()) < 100) and HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(pdf_path)

            # Check encryption
            if reader.is_encrypted:
                return None, 0, 'encrypted'

            text = ""
            page_count = len(reader.pages)

            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue
        except Exception as e:
            return None, 0, f'corrupted: {str(e)[:100]}'

    if text and len(text.strip()) >= 50:
        return text.strip(), page_count, 'success'
    elif text and len(text.strip()) < 50:
        return None, page_count, 'scan_or_empty'
    else:
        return None, 0, 'failed'

def is_persian_text(text):
    """بررسی متن فارسی"""
    if not text:
        return False
    persian_range = set(range(0x0600, 0x06FF))
    text_chars = set(ord(c) for c in text[:500])
    persian_count = len(text_chars.intersection(persian_range))
    return persian_count > len(text_chars) * 0.1

def convert_pdfs_to_json(directory_path, output_json_path):
    """تبدیل همه PDF ها به JSON"""

    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ پوشه پیدا نشد: {directory_path}")
        return

    pdf_files = list(directory.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ فایل PDF پیدا نشد")
        return

    print(f"📁 پیدا شد: {len(pdf_files):,} فایل PDF")
    print(f"📚 کتابخانه‌ها: pdfplumber={'✓' if HAS_PDFPLUMBER else '✗'}, pypdf={'✓' if HAS_PYPDF else '✗'}")
    print()

    converted_data = []
    stats = {
        'successful': 0,
        'failed': 0,
        'encrypted': 0,
        'corrupted': 0,
        'scan_or_empty': 0
    }

    for idx, pdf_file in enumerate(pdf_files, 1):
        # نمایش پیشرفت
        if idx % 200 == 0 or idx <= 10:
            print(f"⏳ [{idx:,}/{len(pdf_files):,}]")

        try:
            text, page_count, status = extract_text_robust(pdf_file)

            if status == 'success':
                language = "persian" if is_persian_text(text) else "mixed"

                doc = {
                    "id": f"doc_{stats['successful'] + 1}",
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
                stats['successful'] += 1
            elif status == 'encrypted':
                stats['encrypted'] += 1
            elif status.startswith('corrupted'):
                stats['corrupted'] += 1
            elif status == 'scan_or_empty':
                stats['scan_or_empty'] += 1
            else:
                stats['failed'] += 1

        except Exception as e:
            stats['failed'] += 1
            continue

    # ذخیره کردن
    output_path = Path(output_json_path)
    print(f"\n💾 در حال ذخیره...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)

    # آمار
    total_chars = sum(len(doc['text']) for doc in converted_data)
    total_words = sum(doc['metadata']['word_count'] for doc in converted_data)

    print("\n" + "="*70)
    print("✅ تکمیل شد!")
    print("="*70)
    print(f"✓ موفق: {stats['successful']:,} فایل ({stats['successful']*100//len(pdf_files)}%)")
    print(f"✗ ناموفق: {stats['failed'] + stats['encrypted'] + stats['corrupted'] + stats['scan_or_empty']:,} فایل")
    print(f"  - رمزگذاری شده: {stats['encrypted']:,}")
    print(f"  - خراب: {stats['corrupted']:,}")
    print(f"  - اسکن شده/خالی: {stats['scan_or_empty']:,}")
    print(f"  - سایر خطاها: {stats['failed']:,}")
    print(f"\n✓ کاراکتر کل: {total_chars:,}")
    print(f"✓ کلمه کل: {total_words:,}")
    print(f"✓ خروجی: {output_path}")
    print(f"✓ حجم فایل: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print("="*70)

if __name__ == "__main__":
    source_dir = "/home/amirxo/Desktop/New Folder 2"
    output_file = "/home/amirxo/git/pdf_training_data.json"

    print("="*70)
    print("🔄 تبدیل PDF به JSON")
    print("="*70)
    print(f"📂 منبع: {source_dir}")
    print(f"📄 خروجی: {output_file}")
    print("="*70)
    print()

    convert_pdfs_to_json(source_dir, output_file)

