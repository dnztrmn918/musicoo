import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API_ID yoksa veya hatalıysa botun çökmesini engellemek için kontrol
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    STRING_SESSION = os.getenv("STRING_SESSION", "")

    if not API_ID or not API_HASH:
        print("❌ HATA: API_ID veya API_HASH .env dosyasında bulunamadı!")
