# راهنمای پیکربندی Extension های Cursor IDE

این فایل شامل توضیحات و تنظیمات بهینه برای Extension های نصب شده در Cursor IDE است.

## 📋 Extension های نصب شده

### 1. Python & CursorPyright
- **Extension**: `ms-python.python` و `anysphere.cursorpyright`
- **وظیفه**: پشتیبانی کامل از Python و نوع‌یابی
- **تنظیمات بهینه**:
  - استفاده از `Pylance` به عنوان language server
  - فعال کردن type checking
  - فعال کردن auto imports

### 2. ESLint
- **Extension**: `dbaeumer.vscode-eslint`
- **وظیفه**: بررسی کد JavaScript/TypeScript
- **تنظیمات بهینه**:
  - فعال‌سازی format
  - اجرای خودکار هنگام تایپ

### 3. Prettier
- **Extension**: `esbenp.prettier-vscode`
- **وظیفه**: فرمت‌بندی خودکار کد
- **تنظیمات بهینه**:
  - فرمت خودکار هنگام ذخیره
  - پشتیبانی از تمام زبان‌های مدرن

### 4. GitLens
- **Extension**: `eamodio.gitlens`
- **وظیفه**: تقویت Git در IDE
- **تنظیمات بهینه**:
  - نمایش blame در خط کنونی
  - نمایش تاریخچه commit
  - نمایش author و زمان

### 5. Error Lens
- **Extension**: `usernamehw.errorlens`
- **وظیفه**: نمایش خطاها و هشدارها در خطوط کد
- **تنظیمات بهینه**:
  - نمایش error و warning
  - گزینه‌های مرئی

### 6. Tailwind CSS
- **Extension**: `bradlc.vscode-tailwindcss`
- **وظیفه**: IntelliSense برای Tailwind CSS
- **تنظیمات بهینه**:
  - پشتیبانی از `cva` و `cn` utilities
  - تکمیل خودکار کلاس‌ها

### 7. Rust Analyzer
- **Extension**: `rust-lang.rust-analyzer`
- **وظیفه**: Language Server برای Rust
- **تنظیمات بهینه**:
  - فعال کردن type hints
  - بررسی همه targets
  - فعال کردن lifetime hints

### 8. Go
- **Extension**: `golang.go`
- **وظیفه**: پشتیبانی از زبان Go
- **تنظیمات بهینه**:
  - استفاده از `goimports` برای فرمت
  - استفاده از `golangci-lint` برای linting

### 9. Java
- **Extension**: `redhat.java` و `vscjava.vscode-java-debug`
- **وظیفه**: پشتیبانی از Java و Spring Boot
- **تنظیمات بهینه**:
  - به‌روزرسانی خودکار تنظیمات build
  - سازمان‌دهی خودکار imports

### 10. Docker
- **Extension**: `ms-azuretools.vscode-docker`
- **وظیفه**: مدیریت Docker و containers
- **تنظیمات بهینه**:
  - فعال‌سازی linting برای Dockerfile
  - پشتیبانی از Docker Compose

### 11. Kubernetes
- **Extension**: `ms-kubernetes-tools.vscode-kubernetes-tools`
- **وظیفه**: مدیریت Kubernetes
- **تنظیمات بهینه**:
  - پشتیبانی از kubectl

### 12. Git Graph
- **Extension**: `mhutchie.git-graph`
- **وظیفه**: نمایش گرافیکی Git history
- **تنظیمات بهینه**: نمایش درست

### 13. Git History
- **Extension**: `donjayamanne.githistory`
- **وظیفه**: مشاهده تاریخچه فایل‌ها

### 14. Auto Rename Tag
- **Extension**: `formulahendry.auto-rename-tag`
- **وظیفه**: تغییر خودکار تگ‌های HTML/JSX
- **تنظیمات بهینه**:
  - فعال در تمام زبان‌های مربوطه

### 15. Path IntelliSense
- **Extension**: `christian-kohler.path-intellisense`
- **وظیفه**: تکمیل خودکار مسیرها

### 16. SonarLint
- **Extension**: `sonarsource.sonarlint-vscode`
- **وظیفه**: تحلیل کیفیت کد
- **تنظیمات بهینه**: استفاده بهینه

### 17. Crates
- **Extension**: `serayuzgur.crates`
- **وظیفه**: مدیریت Cargo.toml در Rust
- **تنظیمات بهینه**:
  - به‌روزرسانی خودکار نسخه‌ها

### 18. Auto Docstring
- **Extension**: `njpwerner.autodocstring`
- **وظیفه**: ایجاد خودکار docstring برای Python

### 19. Python Indent
- **Extension**: `kevinrose.vsc-python-indent`
- **وظیفه**: بهبود indentation در Python

## ⚙️ تنظیمات کلیدی

### جلوگیری از Bug های رایج:

1. **Python**:
   - استفاده از Pylance به جای Jedi
   - فعال کردن type checking
   - استفاده از black برای formatting

2. **JavaScript/TypeScript**:
   - استفاده از ESLint و Prettier
   - تنظیم import paths به relative
   - فعال‌سازی formatOnSave

3. **Rust**:
   - استفاده از rust-analyzer
   - فعال کردن درlays
   - بررسی همه targets

4. **Go**:
   - استفاده از goimports
   - استفاده از golangci-lint
   - فعال کردن go.useLanguageServer

5. **Git**:
   - فعال کردن auto fetch
   - استفاده از GitLens برای view بهتر
   - استفاده از Git Graph برای history

## 🔧 راه‌اندازی

تمام تنظیمات در فایل زیر ذخیره شده‌اند:
```
/home/amirxo/.cursor/User/settings.json
```

## 📝 نکات مهم

1. تله‌متری غیرفعال است برای حفظ حریم خصوصی
2. Auto-save فعال است با تاخیر 1 ثانیه
3. File exclusion برای بهبود عملکرد تنظیم شده
4. همه فرمت‌بندی‌ها روی save اعمال می‌شوند
5. Git auto-fetch هر 3 دقیقه اجرا می‌شود

## 🚀 استفاده

- برای استفاده از extension ها:
  - پوشش `Ctrl+Shift+X` باز می‌شود
  - یک زبان را تایپ کنید و extension مربوطه را نصب کنید

- برای تنظیمات بیشتر:
  - `Ctrl+Shift+P` را باز کنید
  - "Preferences: Open Settings (JSON)" را تایپ کنید

## 🎯 تنظیمات تکمیلی

### ماشه‌های کلیدی:
- **F5**: شروع debug
- **Shift+F5**: توقف debug
- **F9**: toggle breakpoint
- **F10**: step over
- **F11**: step into
- **Shift+F11**: step out

### Tasks:
- **Ctrl+Shift+C**: بررسی syntax
- **Ctrl+Shift+L**: Lint کد
- **Ctrl+Shift+F**: فرمت فایل‌ها
- **Ctrl+Shift+A**: اجرای تمام چک‌ها
- **Ctrl+Shift+T**: بررسی نوع TypeScript

## 🔍 رفع مشکلات

### اگر extension کار نمی‌کند:
1. Extension را reload کنید (Ctrl+Shift+P -> "Reload Window")
2. بررسی کنید که تنظیمات درست اعمال شده‌اند
3. بررسی کنید که زبان مربوطه در فایل فعال است

### مشکلات رایج:
- **Python imports**: بررسی کنید که virtualenv فعال است
- **TypeScript errors**: بررسی کنید که tsconfig.json وجود دارد
- **Rust errors**: بررسی کنید که cargo در PATH است

## 📚 منابع اضافی

- [Documentation VS Code Extensions](https://code.visualstudio.com/docs/editor/extension-marketplace)
- [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Rust Analyzer](https://rust-analyzer.github.io/)
- [GitLens Documentation](https://gitlens.amod.io/)

## ✅ لیست بررسی

- [x] تنظیمات Python
- [x] تنظیمات JavaScript/TypeScript
- [x] تنظیمات Rust
- [x] تنظیمات Go
- [x] تنظیمات Git
- [x] تنظیمات Docker
- [x] تنظیمات Java
- [x] جلوگیری از Bug های رایج
- [x] تنظیم file exclusions
- [x] تنظیم auto-format
- [x] تنظیم telemetry off
- [x] تنظیم extension auto-update
