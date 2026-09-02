from app import create_app, db
import os

app = create_app()

def reset_database():
    with app.app_context():
        # Delete the existing database file (مسیر واقعی رو از تنظیمات
        # SQLAlchemy می‌خونیم، نه یک مسیر ثابت احتمالاً اشتباه)
        db_path = str(db.engine.url.database)
        db.session.close_all()
        db.engine.dispose()
        if db_path and os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        # Create all tables
        db.create_all()
        print("Created new database with updated schema")
        
        # Recreate the default admin user
        from app import ensure_default_admin
        ensure_default_admin()
        print("Recreated default admin user")

if __name__ == '__main__':
    reset_database()
