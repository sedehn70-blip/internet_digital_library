import os
from app import create_app, db
from app import Book

# ساخت اپلیکیشن
app = create_app()

# مسیر پوشه کتاب‌ها
BOOKS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books')

with app.app_context():
    # پیمایش تمام فایل‌های .txt در پوشه
    for filename in os.listdir(BOOKS_DIR):
        if filename.endswith('.txt'):
            filepath = os.path.join(BOOKS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # عنوان کتاب از نام فایل (بدون پسوند)
            title = os.path.splitext(filename)[0]
            # نویسنده به صورت پیش‌فرض
            author = "ناشناس"
            
            # جلوگیری از اضافه شدن کتاب تکراری
            existing = Book.query.filter_by(title=title).first()
            if not existing:
                book = Book(title=title, author=author, content=content)
                db.session.add(book)
    
    db.session.commit()
    print("تمام کتاب‌ها اضافه شدند!")
