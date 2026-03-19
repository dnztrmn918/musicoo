import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    
    # SADECE BURAYI DEĞİŞTİRİYORUZ. Kodu direkt içine gömüyoruz:
    BOT_TOKEN = "8372013267:AAHAcPRWYVclQRsePZVmPwBFqzwP8yfXS8g" 
    
    STRING_SESSION = os.getenv("STRING_SESSION", "")

    if not API_ID or not API_HASH:
        print("❌ HATA: API_ID veya API_HASH .env dosyasında bulunamadı!")
