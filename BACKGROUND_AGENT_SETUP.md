# راهنمای کامل تنظیم Background Agent در Cursor

## مشکل فعلی
Background Agent نمی‌تواند به repository شما دسترسی پیدا کند و خطای "Access Denied: Unauthorized request" نمایش می‌دهد.

## راه حل سریع (مستقیم از Terminal)

### گام 1: گرفتن Token
```bash
gh auth token
```
این token را کپی کنید

### گام 2: اضافه کردن به Cursor
1. در Cursor Settings > Background Agents > Secrets
2. Secret قدیمی "github" را حذف کنید
3. در "Secret name" بنویسید: **GITHUB_TOKEN**
4. Token را در "Secret value" paste کنید
5. روی "Create" کلیک کنید
6. در بخش "GitHub Access" روی "Refresh" بزنید

### گام 3: Enable کردن Agent
در نوار کناری، Agent را ON کنید

