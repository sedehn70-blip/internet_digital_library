import os
from app import create_app, db, Book

# ساخت اپلیکیشن
app = create_app()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with app.app_context():
    books = Book.query.all()
    for book in books:
        # بررسی PDF
        pdf_path = getattr(book, 'pdf_filename', None)
        if pdf_path:
            full_pdf_path = os.path.join(BASE_DIR, 'pdf_books', pdf_path)
            if not os.path.exists(full_pdf_path):
                print(f"پاک شد (PDF): {book.title}")
                db.session.delete(book)
        # بررسی فایل TXT
        else:
            # مسیر پیش‌فرض فایل txt
            txt_path = os.path.join(BASE_DIR, 'books', book.title + '.txt')
            if not os.path.exists(txt_path):
                print(f"پاک شد (TXT): {book.title}")
                db.session.delete(book)

    db.session.commit()
    print("تمام کتاب‌های بدون فایل پاک شدند!")
