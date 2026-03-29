import yt_dlp
import os

def search_youtube(query):
    # Ana dizindeki cookies.txt dosyasını kontrol eder
    cookie_path = "cookies.txt"
    
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "geo_bypass": True,
    }
    
    # Çerez dosyası varsa yükle
    if os.path.exists(cookie_path):
        ydl_opts["cookiefile"] = cookie_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            return {
                "title": info.get('title', 'Bilinmeyen Şarkı'),
                "webpage_url": info.get('webpage_url', ''),
                "file_path": info.get('url'), # YouTube doğrudan yayın linki
                "thumbnail": info.get('thumbnail', '')
            }
        except Exception as e:
            raise Exception(f"YouTube Arama Hatası: {str(e)}")
