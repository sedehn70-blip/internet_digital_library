import os
import sys
from app import create_app, db, Book
from epub_utils import EPUBReader, is_epub

def detect_category(title):
    """Detect category based on title or content (simple implementation)"""
    if not title:
        return 'general'
        
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

def import_txt_file(filepath):
    """Import a single TXT file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print(f"خطا: فایل خالی است: {filepath}")
            return False
            
        title = os.path.splitext(os.path.basename(filepath))[0]
        
        # Check if book already exists
        existing = Book.query.filter(Book.title == title).first()
        if existing:
            print(f"هشدار: کتاب با عنوان '{title}' از قبل وجود دارد.")
            return False
            
        # Create new book
        book = Book(
            title=title,
            author='ناشناخته',
            content=content,
            file_type='txt',
            category=detect_category(title)
        )
        
        db.session.add(book)
        db.session.commit()
        print(f"کتاب TXT با موفقیت اضافه شد: {title}")
        return True
        
    except Exception as e:
        print(f"خطا در پردازش فایل {filepath}: {str(e)}")
        db.session.rollback()
        return False

def import_epub_file(filepath):
    """Import a single EPUB file"""
    try:
        if not is_epub(filepath):
            print(f"خطا: فایل معتبر EPUB نیست: {filepath}")
            return False
            
        reader = EPUBReader(filepath)
        metadata = reader.read_epub()
        
        if not metadata or 'content' not in metadata:
            print(f"خطا: محتوای کتاب قابل استخراج نبود: {filepath}")
            return False
            
        title = metadata.get('title') or os.path.splitext(os.path.basename(filepath))[0]
        author = metadata.get('author', 'ناشناخته')
        content = metadata.get('content', '')
        
        # Check if book already exists
        existing = Book.query.filter(Book.title == title).first()
        if existing:
            print(f"هشدار: کتاب با عنوان '{title}' از قبل وجود دارد.")
            return False
            
        # Create new book
        book = Book(
            title=title,
            author=author,
            content=content,
            file_type='epub',
            category=detect_category(title)
        )
        
        db.session.add(book)
        db.session.commit()
        print(f"کتاب EPUB با موفقیت اضافه شد: {title} - {author}")
        return True
        
    except Exception as e:
        print(f"خطا در پردازش فایل EPUB {filepath}: {str(e)}")
        db.session.rollback()
        return False

def import_books_from_directory(directory):
    """Import all supported books from a directory"""
    if not os.path.isdir(directory):
        print(f"خطا: مسیر نامعتبر است: {directory}")
        return
        
    success_count = 0
    error_count = 0
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        try:
            if filename.lower().endswith('.txt'):
                if import_txt_file(filepath):
                    success_count += 1
                else:
                    error_count += 1
                    
            elif filename.lower().endswith('.epub'):
                if import_epub_file(filepath):
                    success_count += 1
                else:
                    error_count += 1
                    
        except Exception as e:
            print(f"خطای ناشناخته در پردازش فایل {filename}: {str(e)}")
            error_count += 1
    
    print(f"\nنتیجه نهایی:")
    print(f"- تعداد کتاب‌های با موفقیت اضافه شده: {success_count}")
    print(f"- تعداد خطاها: {error_count}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("کاربری: python import_books_enhanced.py <مسیر_پوشه_کتاب‌ها>")
        sys.exit(1)
        
    directory = sys.argv[1]
    
    # Create app context
    app = create_app()
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Import books from the specified directory
        import_books_from_directory(directory)
