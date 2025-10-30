# 📚 تبدیل‌کننده PDF به JSON برای ParsBERT

## 🎯 هدف
تبدیل اسناد حقوقی فارسی از PDF به JSON ساختاریافته برای آموزش مدل ParsBERT

## ⚠️ سیاست ZERO TOLERANCE

این پروژه تحت سیاست **بدون تحمل** اجرا می‌شود:

- ❌ **هیچ داده جعلی** قابل قبول نیست
- ❌ **هیچ placeholder** استفاده نشود
- ❌ **هیچ شبیه‌سازی** مجاز نیست
- ✅ **فقط داده‌های واقعی** از PDF استخراج می‌شود

## 📦 نصب

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# یا به صورت دستی
pip install PyPDF2
```

## 🚀 استفاده

### روش 1: اجرای مستقیم
```bash
python parsbert_converter.py
```

### روش 2: استفاده از اسکریپت
```bash
chmod +x run.sh
./run.sh
```

## 📁 ساختار پوشه‌ها

```
/home/amirxo/Desktop/pdf/
├── *.pdf                           # فایل‌های ورودی PDF
├── output_json/                    # خروجی‌های JSON
│   ├── document1_parsed.json
│   └── document2_parsed.json
└── logs/                           # لاگ‌ها
    ├── conversion_report.log
    ├── failed_files.log
    ├── integrity_warnings.log
    └── _FINAL_SUMMARY.json
```

## 🔧 تنظیمات

تمام تنظیمات در `config.json` قابل تغییر است:

- مسیر پوشه‌ها
- حد آستانه یکپارچگی
- حداکثر طول پاراگراف
- قوانین نرمال‌سازی

## 📊 خروجی JSON

هر فایل PDF به JSON زیر تبدیل می‌شود:

```json
{
  "meta_data": {
    "source_file": "document.pdf",
    "extraction_date": "2025-10-29T...",
    "language": "fa",
    "original_text_length": 5420,
    "normalized_text_length": 5380
  },
  "title": "عنوان سند",
  "body_text": "متن کامل نرمال‌شده...",
  "paragraphs": [
    {
      "id": 1,
      "text": "پاراگراف اول...",
      "char_count": 856
    }
  ],
  "entities": {
    "legal_terms": ["ماده ۵", "بند ۳"],
    "dates": ["1403/07/08"],
    "numbers": ["ماده ۱۰"]
  },
  "integrity_score": 0.95
}
```

## 🛡️ اعتبارسنجی

سیستم اعتبارسنجی سخت‌گیرانه:

1. **تشخیص داده جعلی**: هر placeholder یا lorem ipsum شناسایی می‌شود
2. **بررسی کامل بودن**: حداقل 95% متن باید استخراج شود
3. **تایید entities**: تمام entities باید در متن اصلی وجود داشته باشند
4. **محاسبه integrity_score**: امتیاز واقعی بر اساس معیارهای دقیق

## 📈 معیارهای یکپارچگی

- **کامل بودن متن**: 40%
- **کیفیت پاراگراف**: 25%
- **استخراج entities**: 20%
- **نرمال‌سازی**: 15%

حد آستانه: **0.85**

## 🚨 رفع مشکلات

### PDF پردازش نمی‌شود
- بررسی کنید PDF رمزدار نباشد
- بررسی کنید PDF اسکن‌شده نباشد (نیاز به OCR)

### integrity_score پایین است
- PDF ممکن است کیفیت پایین داشته باشد
- متن کامل استخراج نشده (احتمالاً تصویر است)

### فایل در لاگ failed_files قرار گرفت
- دلیل دقیق در فایل لاگ نوشته شده
- کدهای خطا:
  - `EXTRACTION_FAILED`: خطا در خواندن PDF
  - `OCR_REQUIRED`: PDF اسکن‌شده است
  - `NO_CONTENT`: PDF خالی است
  - `ACCESS_DENIED`: PDF رمزدار است

## 📞 پشتیبانی

در صورت بروز مشکل، فایل `logs/conversion_report.log` را بررسی کنید.

## 🔐 امنیت و حریم خصوصی

- پردازش کاملاً لوکال (بدون ارسال به سرور)
- بدون استفاده از API خارجی
- داده‌ها در سیستم شما باقی می‌ماند
