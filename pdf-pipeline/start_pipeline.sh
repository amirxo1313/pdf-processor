#!/bin/bash

echo "========================================="
echo "🚀 PDF به تصویر - راه‌اندازی Pipeline"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker در حال اجرا نیست!"
    echo ""
    echo "لطفا ابتدا Docker را راه‌اندازی کنید:"
    echo "  sudo systemctl start docker"
    echo ""
    echo "سپس دوباره این اسکریپت را اجرا کنید."
    exit 1
fi

echo "✅ Docker در حال اجرا است"
echo ""

# Check if PDFs exist
PDF_COUNT=$(ls ~/Desktop/PDF/*.pdf 2>/dev/null | wc -l)
if [ $PDF_COUNT -eq 0 ]; then
    echo "⚠️  هیچ فایل PDF در ~/Desktop/PDF/ پیدا نشد!"
    exit 1
fi

echo "📄 تعداد فایل‌های PDF پیدا شده: $PDF_COUNT"
echo ""

# Run the main script
echo "🔨 شروع فرآیند تبدیل..."
echo "================================="
./run.sh

echo ""
echo "✨ برای بررسی نتایج:"
echo "  ls -la output/"

