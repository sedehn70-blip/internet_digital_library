from app import create_app, db
from app.models import Book

app = create_app()
app.app_context().push()

books = Book.query.all()
for book in books:
    print(f"ID: {book.id}, Title: {book.title}, Category: {book.category}, PDF Filename: {book.pdf_filename}")