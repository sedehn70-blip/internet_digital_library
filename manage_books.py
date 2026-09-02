import os
from app import create_app, db, Book

app = create_app()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALL_BOOKS_DIR = os.path.join(BASE_DIR, 'all_books')

if not os.path.exists(ALL_BOOKS_DIR):
    print("پوشه all_books وجود ندارد! بسازید و کتاب‌ها را داخلش بریزید.")
    exit()

with app.app_context():
    # --- اضافه کردن کتاب‌های جدید ---
    for root, dirs, files in os.walk(ALL_BOOKS_DIR):
        category = os.path.relpath(root, ALL_BOOKS_DIR)
        if category == ".":
            category = None
        for filename in files:
            filepath = os.path.join(root, filename)
            title = os.path.splitext(filename)[0]
            author = "ناشناس"
            existing = Book.query.filter_by(title=title).first()
            if not existing:
                if filename.lower().endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    book = Book(title=title, author=author, content=content, category=category)
                    db.session.add(book)
                    print(f"اضافه شد: {title} (TXT)")
                elif filename.lower().endswith('.pdf'):
                    book = Book(title=title, author=author, pdf_filename=filename, category=category)
                    db.session.add(book)
                    print(f"اضافه شد: {title} (PDF)")

    db.session.commit()

    # --- پاک کردن کتاب‌هایی که فایلشان حذف شده ---
    books = Book.query.all()
    for book in books:
        if book.pdf_filename:
            path = os.path.join(ALL_BOOKS_DIR, book.category or '', book.pdf_filename)
        else:
            path = os.path.join(ALL_BOOKS_DIR, book.category or '', book.title + '.txt')

        if not os.path.exists(path):
            print(f"پاک شد: {book.title}")
            db.session.delete(book)

    db.session.commit()
    print("مدیریت کتاب‌ها کامل شد!")
