import sys
import os

# اضافه کردن پوشه پروژه به ابتدای مسیر
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    # هرگز debug=True رو به‌صورت ثابت ست نکن؛ دیباگر تعاملی Werkzeug اجازه‌ی
    # اجرای کد دلخواه از طریق مرورگر رو می‌ده و نباید در دسترس کاربر نهایی باشه.
    # این فایل (run.py) همون فایلیه که run_app.bat واقعاً اجرا می‌کنه، پس این
    # مقدار مستقیماً روی سرور واقعی اثر می‌ذاره. برای فعال‌سازی دیباگ در توسعه
    # به‌صورت موقت، متغیر محیطی FLASK_DEBUG=1 رو قبل از اجرا ست کن.
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode)