#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخیص مشکلات PDF ها - پیدا کردن دلیل اینکه چرا تبدیل نمی‌شوند
"""

import json
from pathlib import Path
from collections import defaultdict

# Check available libraries
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

def diagnose_single_pdf(pdf_path):
    """تشخیص مشکل یک PDF"""
    result = {
        'filename': pdf_path.name,
        'path': str(pdf_path),
        'error_type': None,
        'error_message': None,
        'page_count': 0,
        'text_length': 0,
        'details': {}
    }

    # 1. چک کردن اندازه فایل
    try:
        file_size = pdf_path.stat().st_size
        result['details']['file_size_kb'] = file_size / 1024
    except Exception as e:
        result['error_type'] = 'file_access_error'
        result['error_message'] = str(e)
        return result

    # 2. چک کردن با PyPDF
    if HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(pdf_path)

            # Check encryption
            if reader.is_encrypted:
                result['error_type'] = 'encrypted'
                result['error_message'] = 'PDF is encrypted'
                return result

            # Check page count
            result['page_count'] = len(reader.pages)

            if result['page_count'] == 0:
                result['error_type'] = 'empty'
                result['error_message'] = 'No pages in PDF'
                return result

            # Try to extract text from first few pages
            extracted_chars = 0
            pages_with_text = 0

            for i, page in enumerate(reader.pages[:5]):  # Check first 5 pages
                try:
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 0:
                        extracted_chars += len(page_text)
                        pages_with_text += 1
                except Exception as e:
                    result['details'][f'page_{i}_error'] = str(e)[:100]

            result['text_length'] = extracted_chars
            result['details']['pages_with_text'] = pages_with_text
            result['details']['total_pages_checked'] = min(5, result['page_count'])

            # Classify based on results
            if extracted_chars < 50:
                result['error_type'] = 'scan_or_empty_text'
                result['error_message'] = f'Very little text extracted ({extracted_chars} chars) - likely scanned image or empty'
            else:
                result['error_type'] = 'successful'
                result['error_message'] = 'Text extracted successfully'

        except pypdf.errors.PdfReadError as e:
            result['error_type'] = 'corrupted_pypdf'
            result['error_message'] = f'PyPDF can\'t read: {str(e)[:200]}'
        except Exception as e:
            result['error_type'] = 'unknown_error_pypdf'
            result['error_message'] = str(e)[:200]

    # 3. چک کردن با pdfplumber
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result['details']['pdfplumber_pages'] = len(pdf.pages)
        except Exception as e:
            result['details']['pdfplumber_error'] = str(e)[:200]

    return result

def diagnose_pdfs_folder(folder_path, sample_size=50):
    """تشخیص مشکلات PDF ها در یک پوشه"""

    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ پوشه پیدا نشد: {folder_path}")
        return

    # Get all PDF files
    pdf_files = list(folder.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ فایل PDF پیدا نشد")
        return

    print(f"📁 پیدا شد: {len(pdf_files)} فایل PDF")

    # For large collections, sample first
    if len(pdf_files) > sample_size:
        print(f"📊 نمونه‌گیری: {sample_size} فایل از {len(pdf_files)} فایل")
        sample_files = pdf_files[:sample_size]
    else:
        sample_files = pdf_files
        print(f"📊 پردازش همه {len(pdf_files)} فایل")

    print()

    # Diagnose
    issues_summary = defaultdict(int)
    detailed_results = []

    for idx, pdf_file in enumerate(sample_files, 1):
        print(f"⏳ [{idx}/{len(sample_files)}] {pdf_file.name}")
        result = diagnose_single_pdf(pdf_file)

        issues_summary[result['error_type']] += 1
        detailed_results.append(result)

    # Print summary
    print("\n" + "="*70)
    print("📊 خلاصه نتایج:")
    print("="*70)

    total = len(sample_files)
    for error_type, count in sorted(issues_summary.items(), key=lambda x: -x[1]):
        percentage = (count / total) * 100
        error_label = {
            'successful': '✅ موفق (متن استخراج شد)',
            'scan_or_empty_text': '📷 اسکن شده یا متن خالی',
            'encrypted': '🔒 رمزگذاری شده',
            'empty': '📄 خالی (بدون صفحه)',
            'corrupted_pypdf': '💥 خراب (PyPDF نمی‌خواند)',
            'file_access_error': '🚫 خطای دسترسی',
            None: '❓ نامشخص'
        }.get(error_type, error_type)

        print(f"  {error_label}: {count} فایل ({percentage:.1f}%)")

    print("="*70)

    # Save detailed results
    output_file = Path("/home/amirxo/git/diagnosis_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': dict(issues_summary),
            'details': detailed_results,
            'total_files': total,
            'date': str(Path.cwd())
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 نتایج جزئیات ذخیره شد در: {output_file}")

    # Recommendations
    print("\n" + "="*70)
    print("💡 پیشنهادات:")
    print("="*70)

    if issues_summary['successful'] / total > 0.7:
        print("✅ بیشتر فایل‌ها قابل تبدیل هستند")
        print("   → استفاده از pdfplumber برای استخراج متن")

    if issues_summary['scan_or_empty_text'] / total > 0.5:
        print("⚠️  بیش از نیمی از PDF ها اسکن شده هستند")
        print("   → نیاز به OCR (pytesseract + tesseract-ocr-fas)")

    if issues_summary['corrupted_pypdf'] + issues_summary.get('unknown_error_pypdf', 0) > 0:
        print("⚠️  برخی فایل‌ها خراب هستند")
        print("   → رد کردن فایل‌های خراب و ادامه پردازش")

    print("="*70)

if __name__ == "__main__":
    source_dir = "/home/amirxo/Desktop/New Folder 2"

    print("="*70)
    print("🔍 تشخیص مشکلات PDF ها")
    print("="*70)
    print(f"📂 پوشه: {source_dir}")
    print("="*70)
    print()

    diagnose_pdfs_folder(source_dir, sample_size=100)

