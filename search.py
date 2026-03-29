import yt_dlp
import os

def search_youtube(query):
    # Mevcut dizini ve dosyayı kontrol et
    current_dir = os.getcwd()
    cookie_path = os.path.join(current_dir, "cookies.txt")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "geo_bypass": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    # KESİN KONTROL: Dosya gerçekten orada mı?
    if os.path.exists(cookie_path):
        print(f"🍪 [KONTROL]: cookies.txt bulundu! Konum: {cookie_path}")
        ydl_opts["cookiefile"] = cookie_path
    else:
        print(f"⚠️ [UYARI]: cookies.txt bulunamadı! Aranan konum: {cookie_path}")
        # Eğer bulamazsa ana dizine bir daha bak
        alt_path = "cookies.txt"
        if os.path.exists(alt_path):
            ydl_opts["cookiefile"] = alt_path
            print("🍪 [KONTROL]: cookies.txt kök dizinde bulundu.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"🔍 [ARAMA]: {query} aranıyor...")
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            return {
                "title": info.get('title', 'Bilinmeyen Şarkı'),
                "webpage_url": info.get('webpage_url', ''),
                "file_path": info.get('url'),
                "thumbnail": info.get('thumbnail', '')
            }
        except Exception as e:
            # Hatayı daha detaylı ver ki ne olduğunu görelim
            print(f"❌ [HATA]: YouTube işlemi başarısız: {str(e)}")
            raise Exception(f"YouTube Arama Hatası: {str(e)}")
