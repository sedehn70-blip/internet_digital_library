# mail_utils.py
"""
ابزارهای ارسال ایمیل و ساخت/بررسی توکن‌های یک‌بارمصرف (تأیید ایمیل و
بازیابی رمز عبور).

ارسال واقعی ایمیل فقط وقتی فعال می‌شود که متغیرهای محیطی SMTP_HOST و
SMTP_USERNAME/SMTP_PASSWORD تنظیم شده باشند. در غیر این صورت (مثلاً در
محیط توسعه)، متن ایمیل در لاگ برنامه نوشته می‌شود تا کار توسعه بدون نیاز
به یک سرور SMTP واقعی ادامه پیدا کند — دقیقاً همان الگویی که این پروژه
برای SECRET_KEY هم استفاده می‌کند.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

EMAIL_VERIFY_SALT = 'email-verify-salt'
PASSWORD_RESET_SALT = 'password-reset-salt'


def _get_serializer(app):
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])


def generate_token(app, email, salt):
    return _get_serializer(app).dumps(email, salt=salt)


def verify_token(app, token, salt, max_age_seconds):
    """در صورت معتبر بودن توکن، ایمیل رمزگشایی‌شده را برمی‌گرداند؛ در غیر این
    صورت None (شامل حالت‌های توکن نامعتبر یا منقضی‌شده)."""
    try:
        return _get_serializer(app).loads(token, salt=salt, max_age=max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None


def send_email(app, to_address, subject, html_body, text_body=None):
    """ارسال ایمیل با SMTP. اگر SMTP تنظیم نشده باشد، فقط در لاگ می‌نویسد و
    True برمی‌گرداند (تا جریان برنامه در محیط توسعه قطع نشود)."""
    smtp_host = app.config.get('SMTP_HOST')
    smtp_username = app.config.get('SMTP_USERNAME')
    smtp_password = app.config.get('SMTP_PASSWORD')

    if not smtp_host or not smtp_username or not smtp_password:
        app.logger.warning(
            "[mail_utils] SMTP تنظیم نشده — ایمیل ارسال نشد و فقط لاگ می‌شود.\n"
            f"To: {to_address}\nSubject: {subject}\n{text_body or html_body}"
        )
        return True

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = app.config.get('MAIL_SENDER', smtp_username)
    msg['To'] = to_address
    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(smtp_host, app.config.get('SMTP_PORT', 587), timeout=15) as server:
            if app.config.get('SMTP_USE_TLS', True):
                server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(msg['From'], [to_address], msg.as_string())
        return True
    except Exception as e:
        app.logger.error(f"[mail_utils] خطا در ارسال ایمیل به {to_address}: {e}")
        return False


def send_verification_email(app, user):
    token = generate_token(app, user.email, EMAIL_VERIFY_SALT)
    base_url = app.config.get('SITE_BASE_URL') or ''
    from flask import url_for
    link = (base_url + url_for('verify_email', token=token)) if base_url else url_for('verify_email', token=token, _external=True)
    html = f"""
    <div dir="rtl" style="font-family: Tahoma, sans-serif;">
        <p>سلام {user.username} عزیز،</p>
        <p>برای تأیید ایمیل خود در «کتابخانه دیجیتال» روی لینک زیر کلیک کنید:</p>
        <p><a href="{link}">{link}</a></p>
        <p>این لینک تا ۲۴ ساعت معتبر است. اگر این درخواست را شما نداده‌اید، این ایمیل را نادیده بگیرید.</p>
    </div>
    """
    return send_email(app, user.email, 'تأیید ایمیل - کتابخانه دیجیتال', html)


def send_password_reset_email(app, user):
    token = generate_token(app, user.email, PASSWORD_RESET_SALT)
    base_url = app.config.get('SITE_BASE_URL') or ''
    from flask import url_for
    link = (base_url + url_for('reset_password', token=token)) if base_url else url_for('reset_password', token=token, _external=True)
    html = f"""
    <div dir="rtl" style="font-family: Tahoma, sans-serif;">
        <p>سلام {user.username} عزیز،</p>
        <p>برای تنظیم رمز عبور جدید روی لینک زیر کلیک کنید:</p>
        <p><a href="{link}">{link}</a></p>
        <p>این لینک تا ۱ ساعت معتبر است. اگر این درخواست را شما نداده‌اید، این ایمیل را نادیده بگیرید و رمز عبور شما تغییر نخواهد کرد.</p>
    </div>
    """
    return send_email(app, user.email, 'بازیابی رمز عبور - کتابخانه دیجیتال', html)
