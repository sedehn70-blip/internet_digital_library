#!/usr/bin/env bash
# scripts/backup_db.sh
#
# بکاپ خودکار دیتابیس. به‌صورت خودکار تشخیص می‌ده الان SQLite داری (وضعیت
# فعلی) یا PostgreSQL (بعد از مهاجرت) و بر همون اساس عمل می‌کنه.
# بکاپ‌های قدیمی‌تر از ۱۴ روز خودکار پاک می‌شن.
#
# اجرای دستی:      bash scripts/backup_db.sh
# اجرای زمان‌بندی‌شده (روی سرور، نه docker): با cron هر شب ساعت ۳ بامداد:
#   0 3 * * *  cd /path/to/project && bash scripts/backup_db.sh >> logs/backup.log 2>&1
# داخل docker-compose: با یه سرویس/کانتینر جدا که این اسکریپت رو صدا بزنه،
# یا از قابلیت pg_dump خودِ postgres image استفاده کن.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RETENTION_DAYS=14

mkdir -p "$BACKUP_DIR"

# اگه .env هست، لودش کن تا DATABASE_URL در دسترس باشه
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.env"
    set +a
fi

DB_URL="${DATABASE_URL:-sqlite:///$PROJECT_DIR/data/library.db}"

if [[ "$DB_URL" == postgresql://* ]] || [[ "$DB_URL" == postgres://* ]]; then
    echo "[backup] حالت PostgreSQL تشخیص داده شد."
    OUT_FILE="$BACKUP_DIR/library_${TIMESTAMP}.sql.gz"
    # pg_dump مقادیر رو مستقیم از DATABASE_URL می‌خونه
    pg_dump "$DB_URL" | gzip > "$OUT_FILE"
    echo "[backup] ذخیره شد: $OUT_FILE"
else
    echo "[backup] حالت SQLite تشخیص داده شد."
    SQLITE_PATH="${DB_URL#sqlite:///}"
    if [ ! -f "$SQLITE_PATH" ]; then
        echo "[backup] فایل دیتابیس پیدا نشد: $SQLITE_PATH" >&2
        exit 1
    fi
    OUT_FILE="$BACKUP_DIR/library_${TIMESTAMP}.db"
    # از دستور .backup در sqlite3 استفاده می‌کنیم (safe حتی وقتی برنامه در حال نوشتنه)
    sqlite3 "$SQLITE_PATH" ".backup '$OUT_FILE'"
    gzip "$OUT_FILE"
    echo "[backup] ذخیره شد: ${OUT_FILE}.gz"
fi

# پاک کردن بکاپ‌های قدیمی‌تر از RETENTION_DAYS روز
find "$BACKUP_DIR" -type f -mtime +"$RETENTION_DAYS" -delete
echo "[backup] بکاپ‌های قدیمی‌تر از $RETENTION_DAYS روز پاک شدن."
