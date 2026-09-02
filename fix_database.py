import os
from app import create_app, db


def reset_database():
    # Create the Flask app
    app = create_app()

    with app.app_context():
        # مسیر واقعی دیتابیس رو مستقیم از تنظیمات SQLAlchemy می‌خونیم (همون
        # چیزی که create_app() واقعاً استفاده می‌کنه: data/library.db یا
        # هرچی که DATABASE_URL ست کرده باشه) به‌جای یک مسیر ثابت و احتمالاً
        # اشتباه، تا این اسکریپت واقعاً همون فایلی رو پاک کنه که برنامه
        # ازش استفاده می‌کنه.
        db_path = str(db.engine.url.database)
        print(f"Database path: {db_path}")

        # Close all database connections
        db.session.close_all()
        db.engine.dispose()

        # Remove the database file if it exists
        if db_path and os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Removed existing database: {db_path}")
            except Exception as e:
                print(f"Error removing database file: {e}")
                return False

        # Ensure the containing folder exists
        if db_path:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create all tables
        try:
            db.create_all()
            print("Created new database with updated schema")

            # ساخت ادمین پیش‌فرض با همون تابع امن خود برنامه (هش bcrypt +
            # پسورد تصادفی امن که در لاگ/کنسول چاپ می‌شه) به‌جای ست کردن
            # دستیِ password_hash='admin' (که نه هش بود، نه امن، و باعث
            # خطا موقع لاگین هم می‌شد).
            from app import ensure_default_admin
            ensure_default_admin()
            print("Created default admin user (see log/console above for credentials)")

            return True
        except Exception as e:
            print(f"Error creating new database: {e}")
            return False


if __name__ == '__main__':
    # Stop any running Flask apps
    print("Stopping any running Flask applications...")
    os.system('taskkill /F /IM python.exe 2>nul')
    os.system('taskkill /F /IM pythonw.exe 2>nul')

    # Reset the database
    print("Resetting database...")
    if reset_database():
        print("✅ Database reset successfully!")
        print("You can now start the application with: python run.py")
    else:
        print("❌ Failed to reset database. Please check the error messages above.")
