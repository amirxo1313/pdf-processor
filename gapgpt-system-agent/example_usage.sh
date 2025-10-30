#!/bin/bash
# GapGPT System Agent - Example Usage Script
# این اسکریپت مثال‌های عملی استفاده از API را نشان می‌دهد

BASE_URL="http://localhost:8000"

echo "🧠 GapGPT System Agent - Examples"
echo "=================================="
echo ""

# 1. بررسی سلامت سیستم
echo "1️⃣ بررسی سلامت سیستم:"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# 2. اطلاعات Agent
echo "2️⃣ اطلاعات Agent:"
curl -s "$BASE_URL/about" | python3 -m json.tool | head -20
echo ""
echo ""

# 3. اجرای دستور سیستم
echo "3️⃣ اجرای دستور سیستم (uname -a):"
curl -s -X POST "$BASE_URL/system/run" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "uname -a"}' | python3 -m json.tool
echo ""
echo ""

# 4. بررسی فضای دیسک
echo "4️⃣ بررسی فضای دیسک:"
curl -s -X POST "$BASE_URL/system/run" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "df -h"}' | python3 -m json.tool
echo ""
echo ""

# 5. لیست کانتینرهای Docker
echo "5️⃣ لیست کانتینرهای Docker:"
curl -s -X POST "$BASE_URL/docker/containers" | python3 -m json.tool | head -30
echo ""
echo ""

# 6. دریافت IP محلی
echo "6️⃣ دریافت IP محلی:"
curl -s "$BASE_URL/net/local-ip" | python3 -m json.tool
echo ""
echo ""

echo "✅ تمام مثال‌ها با موفقیت اجرا شد!"
echo ""
echo "💡 برای استفاده از AI، از endpoint /ask استفاده کنید"


