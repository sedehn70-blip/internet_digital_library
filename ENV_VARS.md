# متغیرهای محیطی (Environment Variables)

این فایل متغیرهای محیطی مربوط به تغییرات امنیتی اخیر رو مستند می‌کنه.
هیچ‌کدوم اجباری برای اجرای محلی/توسعه نیستن (برنامه با مقادیر پیش‌فرض
امن اجرا می‌شه)، ولی برای production باید حتماً تنظیم بشن.

## اجباری در production

| متغیر | توضیح |
|---|---|
| `APP_ENV` | باید برابر `production` باشه تا حالت production فعال بشه (بررسی اجباری بودن SECRET_KEY، فعال شدن HSTS، secure cookies و ...). |
| `SECRET_KEY` | یک مقدار تصادفی و ثابت. تولید: `python -c "import secrets; print(secrets.token_hex(32))"` — این مقدار رو جایی امن نگه دارید و هیچ‌وقت عوضش نکنید مگر بخواید همه‌ی کاربرها logout بشن. |

اگه `APP_ENV=production` باشه ولی `SECRET_KEY` تنظیم نشده باشه، برنامه
اصلاً بالا نمیاد (به‌جای این‌که با یه کلید تصادفی موقت اجرا بشه).

## توصیه‌شده در production

| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/library.db` | برای مهاجرت به PostgreSQL: `postgresql://user:pass@host:5432/dbname` |
| `SESSION_COOKIE_SECURE` | `true` وقتی `APP_ENV=production`، وگرنه `false` | اگه سایت پشت یه reverse proxy بدون HTTPS مستقیم روی همون هاسته، ممکنه لازم باشه دستی تنظیم بشه. |
| `SITE_BASE_URL` | (خالی — از `url_for(..., _external=True)` استفاده می‌شه) | مثلاً `https://example.com` — برای ساخت لینک‌های داخل ایمیل وقتی برنامه پشت پراکسی/لودبالانسر با پروتکل/هاست متفاوته. |

## ایمیل (SMTP) — برای تأیید ایمیل و بازیابی رمز عبور

اگه این‌ها تنظیم نشن، متن ایمیل به‌جای ارسال واقعی توی لاگ برنامه نوشته
می‌شه (مناسب توسعه، برای production باید تنظیم بشن).

| متغیر | مثال | توضیح |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` یا `smtp.sendgrid.net` | آدرس سرور SMTP |
| `SMTP_PORT` | `587` | پورت SMTP (پیش‌فرض 587 با STARTTLS) |
| `SMTP_USERNAME` | `no-reply@example.com` | یوزرنیم SMTP |
| `SMTP_PASSWORD` | *** | پسورد/App Password SMTP |
| `SMTP_USE_TLS` | `1` | `0` برای غیرفعال کردن STARTTLS |
| `MAIL_SENDER` | `no-reply@example.com` | آدرس فرستنده (اگه ست نشه، از SMTP_USERNAME استفاده می‌شه) |

## نمونه فایل env برای production

```
APP_ENV=production
SECRET_KEY=<خروجی secrets.token_hex(32)>
DATABASE_URL=postgresql://user:pass@localhost:5432/digital_library
SITE_BASE_URL=https://example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=no-reply@example.com
SMTP_PASSWORD=xxxxx
MAIL_SENDER=no-reply@example.com
```
