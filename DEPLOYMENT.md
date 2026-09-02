# نقشه‌ی راه تجاری‌سازی

این فایل وضعیت فعلی رو نشون می‌ده: چی از قبل آماده‌ست، چی همین الان توسط
Claude آماده شد، و چی هنوز نیاز به اقدام واقعی (ثبت‌نام، خرید، کار اداری) داره.

## ✅ از قبل توی کد آماده بود (کشف شد، دست نخورد)
- CSRF protection، rate limiting روی روت‌های حساس
- اجبار SECRET_KEY در production (برنامه بدون این مقدار در production بالا نمیاد)
- کوکی امن (Secure/HttpOnly/SameSite) خودکار در production
- security headers کامل (CSP، X-Frame-Options، HSTS در صورت HTTPS)
- لایه‌ی انتزاعی درگاه پرداخت (`payment_gateway.py`) — سوییچ sandbox↔zibal فقط با یک env var
- پشتیبانی از PostgreSQL از طریق `DATABASE_URL` (نیازی به تغییر کد نبود)
- لاگ‌گیری چرخشی (rotating log) در `logs/`

## 🆕 همین الان اضافه شد (زیرساخت، بدون نیاز به حساب واقعی)
| فایل | کاربرد |
|---|---|
| `.env.example` | راهنمای کامل همه‌ی متغیرهای محیطی، بدون هیچ مقدار واقعی |
| `wsgi.py` | نقطه‌ی ورود برای gunicorn (به‌جای `python app.py` توسعه‌ای) |
| `Dockerfile` | بسته‌بندی برنامه برای اجرای سرور، نه فقط ویندوز |
| `docker-compose.yml` | برنامه + PostgreSQL + nginx با یک دستور |
| `nginx/library.conf.example` | تنظیمات reverse proxy، آماده برای اتصال SSL بعدی |
| `scripts/backup_db.sh` | بکاپ خودکار روزانه (هم SQLite الان، هم PostgreSQL بعداً) |
| Sentry hook در `app.py` | مانیتورینگ خطا؛ کاملاً خاموشه تا `SENTRY_DSN` رو ست کنی |
| `requirements.txt` | اضافه شدن `psycopg2-binary`، `gunicorn`، `sentry-sdk` |

همه‌ی این‌ها **الان بدون هیچ حساب بیرونی هم قابل تست محلیه**:
```bash
cp .env.example .env
docker compose up -d --build
```
با این کار، سایت با PostgreSQL واقعی (نه SQLite) و پشت nginx روی
`http://localhost` بالا میاد — دقیقاً همون چیدمانی که روی سرور واقعی هم
استفاده می‌شه، فقط با دامنه‌ی واقعی به‌جای localhost.

## ⏳ نیاز به اقدام واقعی شما (زمان‌بر، بیرون از کد)

هرکدوم که آماده شد، فقط کافیه مقدار مربوطه رو توی `.env` واقعی (روی سرور)
پر کنی — **هیچ تغییر کدی لازم نیست**، چون همه‌چیز از قبل env-driven طراحی شده.

1. **سرور (VPS)** — خرید یک VPS (مثلاً از یک ارائه‌دهنده‌ی داخلی یا خارجی).
   بعد از اون: نصب Docker روی سرور، کپی پروژه، `docker compose up -d`.
2. **دامنه** — خرید دامنه + تنظیم DNS به IP سرور. بعدش `SITE_BASE_URL`
   و `server_name` توی nginx config رو با دامنه‌ی واقعی پر کن.
3. **SSL** — بعد از دامنه، با `certbot --nginx` (دستور دقیق توی
   `nginx/library.conf.example` نوشته شده) گواهی رایگان بگیر.
4. **ثبت‌نام زیبال** — مرچنت کد واقعی رو بگیر، بعد فقط این دو خط رو در
   `.env` سرور عوض کن:
   ```
   PAYMENT_MODE=zibal
   ZIBAL_MERCHANT=<مرچنت واقعی>
   ```
5. **SMTP واقعی** — یک ایمیل/سرویس ارسال (Gmail App Password، SendGrid و...)
   و پر کردن `SMTP_HOST`/`SMTP_USERNAME`/`SMTP_PASSWORD` در `.env`.
6. **Sentry (اختیاری ولی توصیه‌شده)** — یک پروژه‌ی رایگان در sentry.io بساز
   و `SENTRY_DSN` رو پر کن.

## 🔜 فاز بعدی (بعد از این‌که آنلاین شدید)
موارد مدیریتی که هنوز کد نشدن و بعد از استقرار زیرساخت باید روشون کار کنیم:
- audit log برای اعمال ادمین
- نقش‌های چندگانه‌ی ادمین (نه فقط یک فلگ روشن/خاموش)
- مدیریت مرجوعی/استرداد وجه
- کوپن و تخفیف
