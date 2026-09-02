# add_email_and_profile_image_columns.py
"""
اسکریپت مستقل برای اضافه کردن ستون‌های جدید (email، email_verified،
profile_image) مستقیم به دیتابیس SQLite موجود.

چرا `flask db upgrade` کافی نیست؟
دیتابیس این پروژه هیچ‌وقت واقعاً زیر کنترل Alembic نبوده (جدول
alembic_version در آن وجود ندارد و ستون‌هایی مثل phone_number قبلاً با
اسکریپت‌های دستی مشابه این اضافه شده‌اند، نه از طریق migration). اگر
مستقیم `flask db upgrade` بزنید، روی همون migration اول (phone_number)
خطا می‌گیرید چون آن ستون از قبل وجود دارد.

این اسکریپت idempotent است: هر بار که اجرا بشه فقط ستون‌هایی که هنوز
وجود ندارن رو اضافه می‌کنه و اگه اجرای دوباره بشه، خطا نمی‌ده.

استفاده:
    python add_email_and_profile_image_columns.py
"""
import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'library.db')


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cur.fetchall()]


def index_exists(cur, index_name):
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
    return cur.fetchone() is not None


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ فایل دیتابیس پیدا نشد: {DB_PATH}")
        print("   اگه از DATABASE_URL (مثلاً PostgreSQL) استفاده می‌کنید، این "
              "اسکریپت مخصوص SQLite است و باید معادلش رو با ALTER TABLE دستی بزنید.")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    changed = False

    if not column_exists(cur, 'user', 'email'):
        print("➕ اضافه کردن ستون user.email ...")
        cur.execute("ALTER TABLE user ADD COLUMN email VARCHAR(255)")
        changed = True
    else:
        print("✅ ستون user.email از قبل وجود دارد.")

    if not index_exists(cur, 'uq_user_email'):
        print("➕ ساخت ایندکس یکتا روی user.email ...")
        # UNIQUE INDEX روی مقادیر NULL محدودیتی اعمال نمی‌کنه (چند کاربر
        # می‌تونن هم‌زمان email=NULL داشته باشن)، دقیقاً همون رفتاری که
        # می‌خوایم برای حساب‌های قدیمی بدون ایمیل.
        cur.execute("CREATE UNIQUE INDEX uq_user_email ON user (email)")
        changed = True
    else:
        print("✅ ایندکس uq_user_email از قبل وجود دارد.")

    if not column_exists(cur, 'user', 'email_verified'):
        print("➕ اضافه کردن ستون user.email_verified ...")
        cur.execute("ALTER TABLE user ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT 0")
        changed = True
    else:
        print("✅ ستون user.email_verified از قبل وجود دارد.")

    if not column_exists(cur, 'user_profile', 'profile_image'):
        print("➕ اضافه کردن ستون user_profile.profile_image ...")
        cur.execute("ALTER TABLE user_profile ADD COLUMN profile_image VARCHAR(255)")
        changed = True
    else:
        print("✅ ستون user_profile.profile_image از قبل وجود دارد.")

    con.commit()
    con.close()

    if changed:
        print("\n✅ تمام. دیتابیس به‌روزرسانی شد — حالا می‌تونید سرور رو (دوباره) اجرا کنید.")
    else:
        print("\nℹ️ چیزی برای تغییر نبود، دیتابیس از قبل به‌روز بود.")


if __name__ == '__main__':
    main()
