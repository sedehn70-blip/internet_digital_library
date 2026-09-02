import os
import fitz  # PyMuPDF برای PDF
from app import create_app, db, Book

# ساخت اپلیکیشن
app = create_app()

# مسیر پوشه‌ها
TXT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books')
PDF_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pdf_books')

with app.app_context():
    # ------------------ اضافه کردن کتاب‌های TXT ------------------
    for filename in os.listdir(TXT_DIR):
        if filename.endswith('.txt'):
            filepath = os.path.join(TXT_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = os.path.splitext(filename)[0]
            author = "ناشناس"
            
            existing = Book.query.filter_by(title=title).first()
            if not existing:
                book = Book(title=title, author=author, content=content)
                db.session.add(book)

    # ------------------ اضافه کردن کتاب‌های PDF ------------------
    for filename in os.listdir(PDF_DIR):
        if filename.endswith('.pdf'):
            filepath = os.path.join(PDF_DIR, filename)
            doc = fitz.open(filepath)
            content = ""
            for page in doc:
                content += page.get_text()
            
            title = os.path.splitext(filename)[0]
            author = "ناشناس"
            
            existing = Book.query.filter_by(title=title).first()
            if not existing:
                book = Book(title=title, author=author, content=content, pdf_filename=filename)
                db.session.add(book)

    db.session.commit()
    print("تمام کتاب‌های TXT و PDF اضافه شدند!")
