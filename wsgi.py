# wsgi.py — نقطه‌ی ورود برای اجرای واقعی روی سرور (gunicorn/uwsgi).
#
# app.py از الگوی application factory استفاده می‌کنه (create_app())، برای
# همین برخلاف اجرای محلی (python app.py) نمی‌شه مستقیم به متغیر app توی
# app.py رجوع کرد. این فایل همون کاری رو می‌کنه که بلوک
# `if __name__ == '__main__'` توی app.py می‌کنه، ولی به‌جای Flask dev
# server، خروجی‌اش برای gunicorn/uwsgi قابل استفاده‌ست.
#
# اجرا: gunicorn --bind 0.0.0.0:8000 wsgi:app

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
