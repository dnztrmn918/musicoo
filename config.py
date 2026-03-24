import os
from dotenv import load_dotenv

# Yerel testler için .env dosyasını yükler, sunucuda panel değişkenlerini kullanır.
load_dotenv()

class Config:
    # API_ID'yi alırken olası boşlukları siler (.strip), yoksa varsayılan 0 yapar.
    API_ID = int(os.getenv("API_ID", "0").strip())
    
    # Tüm kritik verileri panelden çeker ve boşluk hatalarını engeller.
    API_HASH = os.getenv("API_HASH", "").strip()
    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    STRING_SESSION = os.getenv("STRING_SESSION", "").strip()

    # Hata kontrolü: Kritik veriler eksikse loglarda uyarır.
    if not API_ID or not API_HASH or not BOT_TOKEN:
        print("⚠️ UYARI: API_ID, API_HASH veya BOT_TOKEN eksik! Lütfen Koyeb panelinden 'Variables' kısmını kontrol edin.")
