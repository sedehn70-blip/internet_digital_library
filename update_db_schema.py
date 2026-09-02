from app import create_app, db
from sqlalchemy import text

app = create_app()

def update_database():
    with app.app_context():
        # Check if the 'description' column exists
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('book')]
        
        # Add 'description' column if it doesn't exist
        if 'description' not in columns:
            print("Adding 'description' column to 'book' table...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE book ADD COLUMN description TEXT'))
                conn.commit()
        
        # Add 'file_type' column if it doesn't exist
        if 'file_type' not in columns:
            print("Adding 'file_type' column to 'book' table...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE book ADD COLUMN file_type VARCHAR(10) DEFAULT "pdf"'))
                conn.commit()
        
        print("Database schema updated successfully!")

if __name__ == '__main__':
    update_database()
