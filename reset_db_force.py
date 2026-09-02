from app import create_app, db
import os
import shutil
from pathlib import Path

app = create_app()

def reset_database():
    with app.app_context():
        # Get the database path (مسیر واقعی رو از تنظیمات SQLAlchemy می‌خونیم،
        # نه یک مسیر ثابت احتمالاً اشتباه)
        db_path = str(db.engine.url.database)
        db_folder = os.path.dirname(db_path) if db_path else app.instance_path

        print(f"Database path: {db_path}")

        # Close all database connections
        db.session.close_all()
        db.engine.dispose()
        
        # Remove the database file if it exists
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Removed existing database: {db_path}")
            except Exception as e:
                print(f"Error removing database file: {e}")
                # Try moving it to a backup instead
                try:
                    backup_path = f"{db_path}.bak"
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(db_path, backup_path)
                    print(f"Moved existing database to backup: {backup_path}")
                except Exception as e2:
                    print(f"Error moving database file: {e2}")
                    return False
        
        # Ensure the instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)
        
        # Remove any SQLAlchemy migration files
        migrations_dir = os.path.join(app.root_path, 'migrations')
        if os.path.exists(migrations_dir):
            try:
                shutil.rmtree(migrations_dir)
                print(f"Removed migrations directory: {migrations_dir}")
            except Exception as e:
                print(f"Warning: Could not remove migrations directory: {e}")
        
        # Create all tables
        try:
            db.create_all()
            print("Created new database with updated schema")
            
            # Recreate the default admin user
            from app import ensure_default_admin
            ensure_default_admin()
            print("Recreated default admin user")
            
            return True
        except Exception as e:
            print(f"Error creating new database: {e}")
            return False

if __name__ == '__main__':
    # Stop any running Flask app
    print("Stopping any running Flask applications...")
    os.system('taskkill /F /IM python.exe 2>nul')
    os.system('taskkill /F /IM pythonw.exe 2>nul')
    
    print("Resetting database...")
    if reset_database():
        print("✅ Database reset successfully!")
    else:
        print("❌ Failed to reset database. Please check the error messages above.")
