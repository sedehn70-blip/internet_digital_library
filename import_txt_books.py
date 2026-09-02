import os
from app import create_app, db, Book

app = create_app()
TXT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books')

def detect_category(title):
    """Detect category based on title or content (simple implementation)"""
    title_lower = title.lower()
    if any(word in title_lower for word in ['رمان', 'داستان', 'داستانی']):
        return 'novel'
    elif any(word in title_lower for word in ['علم', 'تکنولوژی', 'فناوری']):
        return 'science'
    elif any(word in title_lower for word in ['تاریخ', 'تاریخی']):
        return 'history'
    elif any(word in title_lower for word in ['دین', 'مذهبی', 'قرآن', 'احادیث']):
        return 'religion'
    return 'general'

with app.app_context():
    for filename in os.listdir(TXT_DIR):
        if filename.endswith('.txt'):
            try:
                filepath = os.path.join(TXT_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = os.path.splitext(filename)[0]
                author = "ناشناس"
                category = detect_category(title)
                
                existing = Book.query.filter_by(title=title).first()
                if not existing:
                    book = Book(
                        title=title,
                        author=author,
                        content=content,
                        file_type='txt',
                        category=category
                    )
                    db.session.add(book)
                    print(f"کتاب TXT '{title}' با موفقیت اضافه شد (دسته‌بندی: {category})")
            
            except Exception as e:
                print(f"خطا در پردازش فایل {filename}: {str(e)}")
                continue
    
    db.session.commit()
    print("عملیات وارد کردن فایل‌های متنی با موفقیت به پایان رسید!")