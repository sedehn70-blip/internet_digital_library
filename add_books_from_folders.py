import os
from app import create_app, db, Book

# ساخت اپلیکیشن و فعال کردن context
app = create_app()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BOOKS_DIR = os.path.join(BASE_DIR, 'books')  # پوشه اصلی کتاب‌ها

with app.app_context():
    for category_name in os.listdir(BOOKS_DIR):
        category_path = os.path.join(BOOKS_DIR, category_name)
        if not os.path.isdir(category_path):
            continue  # فقط پوشه‌ها

        # پیمایش تمام فایل‌های داخل پوشه
        for filename in os.listdir(category_path):
            filepath = os.path.join(category_path, filename)
            if not os.path.isfile(filepath):
                continue

            # استخراج عنوان از نام فایل (بدون پسوند)
            title = os.path.splitext(filename)[0]
            author = "ناشناس"

            # بررسی فایل تکراری
            existing = Book.query.filter_by(title=title, category=category_name).first()
            if existing:
                print(f"{title} در دسته {category_name} قبلاً اضافه شده است.")
                continue

            # تشخیص نوع فایل
            ext = filename.lower().split('.')[-1]
            if ext == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                book = Book(
                    title=title,
                    author=author,
                    content=content,
                    book_type='txt',
                    category=category_name
                )
            elif ext == 'pdf':
                book = Book(
                    title=title,
                    author=author,
                    pdf_filename=filename,
                    book_type='pdf',
                    category=category_name
                )
            else:
                print(f"{filename} فرمت پشتیبانی نشده است. صرفنظر شد.")
                continue

            db.session.add(book)
            print(f"{title} از دسته {category_name} اضافه شد.")

    db.session.commit()
    print("تمام کتاب‌ها با موفقیت اضافه شدند!")
