# راهنمای اتصال به GitHub

## مشکل چیست؟
Background agent در Cursor نیاز دارد که یک remote repository (آدرس GitHub) برای پروژه تعریف شود تا بتواند تغییرات را به صورت خودکار مدیریت کند.

## راه حل

### 1. ابتدا یک repository در GitHub ایجاد کنید
- به https://github.com بروید
- یک repository جدید ایجاد کنید
- نام و توضیحات مناسب انتخاب کنید

### 2. اتصال به GitHub

#### اگر repository را تازه ساختید، این دستور را اجرا کنید:
\`\`\`bash
git remote add origin https://github.com/USERNAME/REPO_NAME.git
\`\`\`

#### اگر remote قبلاً وجود دارد، ابتدا آن را حذف کنید:
\`\`\`bash
git remote remove origin
git remote add origin https://github.com/USERNAME/REPO_NAME.git
\`\`\`

### 3. Push کردن کد به GitHub
\`\`\`bash
git push -u origin main
\`\`\`

### بررسی وضعیت:
\`\`\`bash
git remote -v
\`\`\`

این دستور آدرس GitHub شما را نمایش می‌دهد.
