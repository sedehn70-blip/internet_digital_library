from app import create_app, db
from app import Book  # Import Book from app instead of models
from datetime import datetime

app = create_app()
with app.app_context():
    # Update all books that don't have a created_at value
    Book.query.filter(Book.created_at.is_(None)).update({Book.created_at: datetime.utcnow()}, synchronize_session=False)
    db.session.commit()
    print("Updated created_at for all books")