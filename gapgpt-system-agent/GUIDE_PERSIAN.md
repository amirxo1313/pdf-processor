# 🧠 راهنمای کامل استفاده از GapGPT System Agent

## 📊 وضعیت کنونی
```bash
✅ سرور: http://localhost:8000
✅ وضعیت: Running & Healthy
✅ Token ها: Configured (server-side only)
```

---

## 🚀 شش روش ارتباط با Agent

### 1️⃣ دستور curl مستقیم
```bash
curl http://localhost:8000/health
```

### 2️⃣ اجرای دستور سیستم
```bash
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "uname -a"}'
```

### 3️⃣ استفاده از AI
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Docker چیست؟", "model": "auto"}'
```

### 4️⃣ اجرای اسکریپت مثال
```bash
./example_usage.sh
```

### 5️⃣ استفاده از Python
```python
import requests

response = requests.post("http://localhost:8000/system/run", 
  json={"cmd": "ls -la"})
print(response.json())
```

### 6️⃣ استفاده از test_api.py
```bash
python3 test_api.py
```

---

## 💡 مثال‌های کاربردی

### مثال 1: بررسی سیستم
```bash
# فضای دیسک
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" -d '{"cmd": "df -h"}'

# حافظه
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" -d '{"cmd": "free -h"}'
```

### مثال 2: سوال از AI درباره Docker
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "بهترین روش بهینه‌سازی Docker چیست؟", "model": "auto"}'
```

### مثال 3: مدیریت کانتینرها
```bash
# لیست
curl -X POST http://localhost:8000/docker/containers

# لاگ
curl -X POST http://localhost:8000/docker/logs \
  -H "Content-Type: application/json" \
  -d '{"container_id": "gapgpt-system-agent"}'
```

---

## 🔧 مدیریت کانتینر
```bash
docker compose up -d      # شروع
docker compose logs -f    # لاگ‌ها
docker compose restart    # راه‌اندازی مجدد
docker compose down       # توقف
```

---

**برای شروع سریع، همین دستور را اجرا کن:**
```bash
./example_usage.sh
```
