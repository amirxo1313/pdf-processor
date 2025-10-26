# تنظیمات Cursor IDE - تکمیل شده ✅

## خلاصه کارهای انجام شده

### 1. پیکربندی Extension ها
- ✅ تنظیمات بهینه برای تمام Extension های نصب شده
- ✅ جلوگیری از Bug های رایج
- ✅ بهینه‌سازی Performance

### 2. فایل‌های ایجاد/به‌روزرسانی شده
- `~/.cursor/User/settings.json` - تنظیمات کامل
- `.cursorignore` - لیست فایل‌های حذف از index
- `EXTENSIONS_CONFIGURATION.md` - راهنمای Extension ها

### 3. Extension های پیکربندی شده

#### Python
- ms-python.python
- anysphere.cursorpyright
- njpwerner.autodocstring
- kevinrose.vsc-python-indent

#### JavaScript/TypeScript
- dbaeumer.vscode-eslint
- esbenp.prettier-vscode
- ms-vscode.vscode-typescript-next

#### Web
- bradlc.vscode-tailwindcss
- formulahendry.auto-rename-tag
- christian-kohler.path-intellisense

#### Rust
- rust-lang.rust-analyzer
- serayuzgur.crates

#### Go
- golang.go

#### Java & Spring
- redhat.java
- vscjava.vscode-java-debug
- vmware.vscode-spring-boot

#### DevOps
- ms-azuretools.vscode-docker
- ms-kubernetes-tools.vscode-kubernetes-tools

#### Git
- eamodio.gitlens
- mhutchie.git-graph
- donjayamanne.githistory

#### Quality
- usernamehw.errorlens
- sonarsource.sonarlint-vscode

### 4. تنظیمات کلیدی
- ✅ Format on save فعال
- ✅ Auto save (1 ثانیه)
- ✅ Type checking فعال
- ✅ Auto imports فعال
- ✅ Error lens فعال
- ✅ GitLens فعال
- ✅ Telemetry غیرفعال

### 5. بهینه‌سازی Performance
- ✅ حذف node_modules از index
- ✅ حذف __pycache__ از index
- ✅ حذف target/ از index
- ✅ حذف dist/ و build/ از index
- ✅ کاهش I/O operations

## نحوه استفاده

### باز کردن تنظیمات
```
Ctrl+Shift+P → "Preferences: Open Settings (JSON)"
```

### بررسی Extension ها
```
Ctrl+Shift+X
```

### Reload کردن Extension ها
```
Ctrl+Shift+P → "Developer: Reload Window"
```

## کلیدهای میانبر

- **F5**: شروع debug
- **Shift+F5**: توقف debug
- **F9**: toggle breakpoint
- **F10**: step over
- **F11**: step into
- **Ctrl+Shift+C**: بررسی syntax
- **Ctrl+Shift+L**: Lint کد
- **Ctrl+Shift+F**: فرمت فایل‌ها

## رفع مشکلات

### Extension کار نمی‌کند
1. Extension را reload کنید
2. Cursor را restart کنید
3. Extension را uninstall/reinstall کنید

### Python imports خطا می‌دهند
1. Virtual environment را فعال کنید
2. Python interpreter را انتخاب کنید
3. Pylance را update کنید

### TypeScript errors
1. tsconfig.json را بررسی کنید
2. TypeScript را update کنید
3. node_modules را install کنید

## پشتیبانی

برای اطلاعات بیشتر، فایل `EXTENSIONS_CONFIGURATION.md` را مطالعه کنید.

---
✅ پیکربندی کامل شده است!
