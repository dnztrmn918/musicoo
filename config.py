import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION = os.getenv("SESSION", "") 

# YENİ EKLENEN VERİTABANI VE YETKİ DEĞİŞKENLERİ
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0")) # Kendi Telegram ID'ni buraya yazacaksın
