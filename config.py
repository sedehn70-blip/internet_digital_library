# config.py
import os
import json
from pathlib import Path

# مسیر فایل تنظیمات
CONFIG_DIR = Path(__file__).parent
PREFERENCES_FILE = CONFIG_DIR / 'user_prefs.json'

# تنظیمات پیش‌فرض
DEFAULT_PREFS = {
    'language': 'farsi',
    'theme': 'default'
}

def load_preferences():
    """بارگذاری تنظیمات کاربر"""
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                return {**DEFAULT_PREFS, **json.load(f)}
        except:
            return DEFAULT_PREFS
    return DEFAULT_PREFS

def save_preferences(prefs):
    """ذخیره تنظیمات کاربر"""
    with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, ensure_ascii=False, indent=4)

# بارگذاری تنظیمات
USER_PREFERENCES = load_preferences()