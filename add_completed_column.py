from app import create_app, db
from flask_migrate import Migrate
import os

def add_completed_column():
    # Create the Flask app
    app = create_app()
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    with app.app_context():
        # Create a migration repository if it doesn't exist
        migrations_dir = os.path.join(app.root_path, 'migrations')
        if not os.path.exists(migrations_dir):
            print("Initializing migrations...")
            os.system('flask db init')
        
        # Create a new migration
        print("Creating migration for adding 'completed' column...")
        os.system('flask db migrate -m "Add completed column to reading_progress"')
        
        # Apply the migration
        print("Applying migration...")
        os.system('flask db upgrade')
        
        print("✅ Migration completed successfully!")

if __name__ == '__main__':
    # Stop any running Flask apps
    print("Stopping any running Flask applications...")
    os.system('taskkill /F /IM python.exe 2>nul')
    os.system('taskkill /F /IM pythonw.exe 2>nul')
    
    # Run the migration
    add_completed_column()
