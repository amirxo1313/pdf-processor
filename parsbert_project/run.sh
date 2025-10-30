#!/bin/bash

set -e

echo "🚀 شروع تبدیل PDF به JSON"
echo "================================"
echo ""

# مسیر اسکریپت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# بررسی وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 نصب نیست!"
    exit 1
fi

# ساخت/استفاده از محیط مجازی محلی
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "🧰 ایجاد محیط مجازی محلی (.venv)..."
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo "❌ خطا در ایجاد محیط مجازی. لطفاً بسته python3-venv را نصب کنید (مثال: sudo apt install python3-venv)"
        exit 1
    fi
fi

# فعال‌سازی محیط مجازی
source "$VENV_DIR/bin/activate"

# ارتقای pip داخل venv
python -m pip install --upgrade pip >/dev/null 2>&1 || true

# بررسی وجود requirements
if [ ! -f "requirements.txt" ]; then
    echo "❌ فایل requirements.txt یافت نشد!"
    deactivate || true
    exit 1
fi

# نصب وابستگی‌ها در venv
echo "📦 نصب وابستگی‌ها در محیط مجازی..."
pip install -q -r requirements.txt

echo ""
echo "⚙️  شروع پردازش..."
echo ""

# اجرای مبدل با پایتون محیط مجازی
python parsbert_converter.py

STATUS=$?

deactivate || true

if [ $STATUS -eq 0 ]; then
    echo ""
    echo "✅ پردازش با موفقیت انجام شد!"
    echo "📁 خروجی‌ها در: /home/amirxo/Desktop/PDF/output_json/"
    echo "📊 گزارش نهایی: /home/amirxo/Desktop/PDF/logs/_FINAL_SUMMARY.json"
else
    echo ""
    echo "❌ خطا در پردازش!"
    echo "🔍 لطفاً لاگ را بررسی کنید: /home/amirxo/Desktop/PDF/logs/conversion_report.log"
    exit $STATUS
fi
