# Dockerfile — بستن برنامه برای اجرای واقعی روی سرور (نه اجرای محلی روی ویندوز)
#
# ساخت ایمیج:   docker build -t digital-library .
# اجرا (تنها):  docker run --env-file .env -p 8000:8000 digital-library
# اجرای کامل (با دیتابیس postgres و nginx): docker compose up -d --build

FROM python:3.11-slim

# وابستگی‌های سیستمی لازم برای weasyprint/pdf2image/matplotlib/psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    poppler-utils \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# pyinstaller/pywin32 مخصوص بسته‌بندی دسکتاپ ویندوز هستن و روی لینوکس/سرور
# لازم نیستن؛ اگه نصبشون خطا داد، از requirements.txt حذفشون کن.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# دایرکتوری‌هایی که برنامه در زمان اجرا بهشون نیاز داره
RUN mkdir -p data logs uploads/covers static/profile_images static/uploads/charts

EXPOSE 8000

ENV APP_ENV=production

# gunicorn به‌جای app.run() توسعه‌ای — چند worker، برای بار واقعی
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "wsgi:app"]
