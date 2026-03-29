import yt_dlp
import os

def search_youtube(query):
    # Platformlar ve yt-dlp içindeki arama kodları
    # scsearch: SoundCloud, jssearch: JioSaavn, deezsearch (veya generic): Deezer alternatifleri
    engines = [
        {"name": "SoundCloud", "code": "scsearch"},
        {"name": "JioSaavn", "code": "jssearch"},
        {"name": "Deezer/Global", "code": "isrc"}, # ISRC üzerinden global kütüphane tarar
        {"name": "YouTube (Yedek)", "code": "ytsearch"} # En son çare YouTube
    ]
    
    for engine in engines:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "default_search": engine["code"],
            "nocheckcertificate": True,
            "geo_bypass": True,
        }
        
        # Sadece YouTube denenirken (eğer varsa) cookies.txt kullan
        if engine["name"] == "YouTube (Yedek)" and os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] üzerinden aranıyor: {query}")
                # Arama yap ve bilgileri çek
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                    
                    # Başarı durumunda bilgileri döndür
                    return {
                        "title": info.get('title', 'Bilinmeyen Parça'),
                        "webpage_url": info.get('webpage_url', ''),
                        "file_path": info.get('url'), # Bu, asistanın çalacağı direkt linktir
                        "thumbnail": info.get('thumbnail', ''),
                        "source": engine['name']
                    }
            except Exception as e:
                print(f"⚠️ {engine['name']} başarısız: {str(e)[:50]}... Sıradakine geçiliyor.")
                continue # Bir sonraki platforma geç

    # Eğer hiçbir platformda bulunamazsa
    raise Exception("❌ Üzgünüm reis; SoundCloud, Saavn, Deezer ve YouTube'da bu şarkıyı bulamadım.")
