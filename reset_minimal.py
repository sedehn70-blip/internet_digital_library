from app import db
import os


def reset_db():
    # Drop all tables
    db.drop_all()
    print("Dropped all tables")

    # Create all tables
    db.create_all()
    print("Created all tables")

    # ساخت ادمین پیش‌فرض با تابع امن خود برنامه (هش bcrypt واقعی، نه متن خام)
    from app import ensure_default_admin
    ensure_default_admin()
    print("Created default admin user (see log/console above for credentials)")


if __name__ == '__main__':
    # Stop any running Flask app
    os.system('taskkill /F /IM python.exe 2>nul')
    os.system('taskkill /F /IM pythonw.exe 2>nul')

    # Set up the app context
    from app import create_app
    app = create_app()

    with app.app_context():
        reset_db()
    print("✅ Database reset successfully!")
