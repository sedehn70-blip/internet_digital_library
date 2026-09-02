<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کتابخانه دیجیتال - مرکز ری شناسی</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* فونت‌ها */
        @font-face {
            font-family: 'BTitr';
            src: url("{{ url_for('static', filename='fonts/B_Titr.ttf') }}");
        }

        @font-face {
            font-family: 'BZar';
            src: url("{{ url_for('static', filename='fonts/B_Zar.ttf') }}");
        }

        /* استایل‌های اصلی */
        body { 
            font-family: 'BZar', Tahoma, sans-serif; 
            background: #f0f2f5; 
            padding-top: 60px;
        }

        .book-title {
            font-family: 'BTitr';
            color: #2c3e50;
            margin-bottom: 1.5rem;
        }

        .book-container { 
            max-width: 900px; 
            margin: auto; 
            background: #fff; 
            border-radius: 20px; 
            padding: 30px; 
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        }

        .txt-content { 
            background: #f8f9fa; 
            border-right: 4px solid #6c63ff;
            padding: 25px;
            border-radius: 12px; 
            max-height: 60vh; 
            overflow-y: auto; 
            margin-bottom: 25px; 
            white-space: pre-wrap; 
            line-height: 2;
            font-size: 1.1rem;
            text-align: justify;
        }

        /* نوار پیشرفت */
        .reading-progress {
            position: fixed;
            top: 0;
            right: 0;
            width: 100%;
            height: 5px;
            background: #e9ecef;
            z-index: 1000;
        }

        .reading-progress-bar {
            height: 100%;
            width: 0%;
            background: #4CAF50;
            transition: width 0.3s ease;
            border-radius: 0 0 0 4px;
        }

        /* دکمه‌ها */
        .btn-save { 
            background: #28a745; 
            border: none; 
            font-weight: 600; 
            transition: all 0.3s;
            padding: 10px 20px;
            border-radius: 8px;
        }

        .btn-save:hover { 
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .btn-back { 
            background: #6c757d; 
            border: none; 
            font-weight: 600; 
            margin-top: 20px; 
            transition: all 0.3s;
            padding: 10px 20px;
            border-radius: 8px;
            width: 100%;
            display: block;
            text-align: center;
        }

        .btn-back:hover { 
            background: #5a6268;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* اسکرول بار */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        /* رسپانسیو */
        @media (max-width: 768px) {
            .book-container {
                margin: 15px;
                padding: 20px;
            }
            
            .txt-content {
                padding: 15px;
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <!-- نوار پیشرفت -->
    <div class="reading-progress">
        <div class="reading-progress-bar" id="readingProgress"></div>
    </div>

    <div class="book-container">
        <h1 class="book-title text-center mb-4">{{ book.title }}</h1>
        <p class="text-muted mb-4 text-center">
            <i class="bi bi-person-fill"></i> {{ book.author or 'ناشناس' }}
            <span class="mx-3">|</span>
            <i class="bi bi-calendar3"></i> {{ book.created_at.strftime('%Y/%m/%d') if book.created_at else '' }}
        </p>

        <div class="txt-content" id="txt-content">
            {{ book.content or 'محتوایی برای نمایش وجود ندارد.' }}
        </div>

        <form method="POST" class="mb-4">
            <div class="d-grid gap-2">
                <button type="submit" class="btn btn-save">
                    <i class="bi bi-bookmark-check"></i> ذخیره پیشرفت
                </button>
            </div>
        </form>

        <a href="{{ url_for('books') }}" class="btn btn-back">
            <i class="bi bi-arrow-right"></i> بازگشت به کتاب‌ها
        </a>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"></script>

    <script>
        // تابع ذخیره پیشرفت
        let saveProgressTimer;
        
        function saveProgress(position) {
            if (saveProgressTimer) {
                clearTimeout(saveProgressTimer);
            }
            
            saveProgressTimer = setTimeout(() => {
                fetch('/api/save_reading_progress', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        book_id: {{ book.id|tojson }},
                        position: position
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // به‌روزرسانی نوار پیشرفت
                        const progressBar = document.getElementById('readingProgress');
                        if (progressBar) {
                            progressBar.style.width = `${position}%`;
                        }
                        
                        // نمایش اعلان ذخیره موفق
                        showNotification('پیشرفت با موفقیت ذخیره شد', 'success');
                    }
                })
                .catch(error => {
                    console.error('خطا در ذخیره پیشرفت:', error);
                    showNotification('خطا در ذخیره پیشرفت', 'error');
                });
            }, 2000); // ذخیره هر 2 ثانیه
        }

        // تابع نمایش اعلان
        function showNotification(message, type = 'info') {
            // ایجاد عنصر اعلان
            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} position-fixed top-3 start-50 translate-middle-x fade show`;
            notification.role = 'alert';
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // اضافه کردن به صفحه
            document.body.appendChild(notification);
            
            // حذف خودکار بعد از 3 ثانیه
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 150);
            }, 3000);
        }

        // مقداردهی اولیه
        document.addEventListener('DOMContentLoaded', function() {
            const txtContent = document.getElementById('txt-content');
            
            // بارگذاری پیشرفت ذخیره شده
            fetch(`/api/get_reading_progress?book_id={{ book.id|tojson }}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.position > 0) {
                        const progressBar = document.getElementById('readingProgress');
                        if (progressBar) {
                            progressBar.style.width = `${data.position}%`;
                        }
                        
                        if (txtContent) {
                            const targetScroll = (data.position / 100) * (txtContent.scrollHeight - txtContent.clientHeight);
                            txtContent.scrollTop = targetScroll;
                        }
                    }
                })
                .catch(console.error);
            
            // ردیابی اسکرول
            if (txtContent) {
                txtContent.addEventListener('scroll', function() {
                    const scrollPercentage = (txtContent.scrollTop / (txtContent.scrollHeight - txtContent.clientHeight)) * 100;
                    if (!isNaN(scrollPercentage) && isFinite(scrollPercentage)) {
                        saveProgress(scrollPercentage);
                    }
                });
            }
            
            // افزودن انیمیشن به محتوای متنی
            const content = txtContent.textContent;
            if (content) {
                txtContent.innerHTML = content.split('\n').map(line => 
                    line ? `<div class="mb-2">${line}</div>` : '<div class="mb-3"></div>'
                ).join('');
            }
            
            // افزودن قابلیت کلیک روی خطوط
            const lines = txtContent.querySelectorAll('div');
            lines.forEach((line, index) => {
                line.style.cursor = 'pointer';
                line.style.transition = 'background-color 0.2s';
                line.onclick = () => {
                    // حاشیه‌گذاری خط انتخاب شده
                    lines.forEach(l => l.style.backgroundColor = 'transparent');
                    line.style.backgroundColor = 'rgba(108, 99, 255, 0.1)';
                    
                    // ذخیره موقعیت خط
                    const position = Math.min(100, Math.max(0, 
                        (index / lines.length) * 100
                    ));
                    saveProgress(position);
                };
            });
        });
    </script>
</body>
</html>