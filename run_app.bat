@echo off
echo در حال نصب پیش‌نیازها...
python -m pip install -r requirements.txt
echo در حال اجرای برنامه...

rem سرور Flask را در یک پنجره جدا و در پس‌زمینه اجرا می‌کنیم تا این اسکریپت
rem بتواند همزمان منتظر آماده شدن سرور بماند (قبلاً مرورگر قبل از بالا آمدن
rem سرور باز می‌شد و باید صفحه را دستی رفرش می‌کردید)
start "کتابخانه دیجیتال - سرور" /min cmd /c "python run.py"

echo در حال آماده‌سازی سرور، لطفاً چند لحظه صبر کنید...
:WAITLOOP
timeout /t 1 /nobreak >nul
curl -s -o nul http://localhost:5000
if errorlevel 1 goto WAITLOOP

rem سرور آماده است، حالا مرورگر باز می‌شود
start http://localhost:5000

echo برنامه با موفقیت اجرا شد.
echo برای بستن کامل برنامه، این پنجره و پنجره سرور را ببندید.
pause
