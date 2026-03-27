import os

# --- TEMEL BOT AYARLARI ---
API_ID = int(os.getenv("API_ID", "0")) # Telegram'dan alınan API ID
API_HASH = os.getenv("API_HASH", "") # Telegram'dan alınan API HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "") # @BotFather'dan alınan Token
SESSION = os.getenv("SESSION", "") # Asistan hesap için Pyrogram String Session

# --- VERİTABANI VE YETKİLER ---
# PostgreSQL bağlantı adresi
DATABASE_URL = os.getenv("DATABASE_URL", "") 

# Sudo kullanıcıları (Komut yetkisi olan ID'ler, virgülle ayırın)
SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip()]

# --- LOG VE İSTATİSTİK AYARLARI ---
# Botun eklendiği grupları bildireceği Grup ID
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1002222222222")) 

# /bilgi komutunun rapor göndereceği Kanal ID
STATS_CHANNEL_ID = int(os.getenv("STATS_CHANNEL_ID", "-1003333333333"))

# --- EKSTRA AYARLAR ---
# Müzik kalitesi veya diğer tercihler buraya eklenebilir
