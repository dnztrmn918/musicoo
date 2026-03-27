import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION = os.getenv("SESSION", "") 

# Veritabanı ve Sudo Ayarları
DATABASE_URL = os.getenv("DATABASE_URL", "") 
SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip()]
