import yt_dlp
import os

def search_youtube(query):
    # Bu dosya bir kez oluştuktan sonra YouTube seni 'yasal cihaz' sayacak
    token_file = "youtube_oauth2.json"
    
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": False, 
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        # --- OAUTH2 SİSTEMİ ---
        "username": "oauth2",
        "password": "", # OAuth2'de şifre boş bırakılır
        "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"🔍 YouTube üzerinden aranıyor: {query}")
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            return {
                "title": info.get('title', 'Bilinmeyen Parça'),
                "webpage_url": info.get('webpage_url', ''),
                "file_path": info.get('url'),
                "thumbnail": info.get('thumbnail', '')
            }
        except Exception as e:
            # Burası altın değerinde; loglarda kodu buradan göreceksin!
            print(f"⚠️ YOUTUBE ONAY GEREKLİ: {str(e)}")
            # Eğer loglarda link ve kod çıkarsa hemen Google'a girip onaylamalısın
            raise Exception("YouTube Onay Bekliyor! Lütfen Koyeb loglarını kontrol et.")
