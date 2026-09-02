# Create a new file called update_db.py
from app import create_app, db
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        # Add the new column if it doesn't exist
        db.engine.execute('ALTER TABLE user ADD COLUMN last_checked_books TIMESTAMP')
        # Set default value for existing users
        db.engine.execute('UPDATE user SET last_checked_books = ?', (datetime.utcnow(),))
        db.session.commit()
        print("Database updated successfully!")
    except Exception as e:
        print("Error updating database:", str(e))