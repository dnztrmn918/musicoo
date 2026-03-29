import yt_dlp
import os

def search_youtube(query):
    # YouTube harici, IP engeli olmayan en sağlam motorlar
    # Sıralamayı değiştirdim: SoundCloud en başta, sonra Saavn ve Bandcamp
    engines = [
        {"name": "SoundCloud", "code": "scsearch1:"},
        {"name": "JioSaavn", "code": "jssearch1:"},
        {"name": "Bandcamp", "code": "bcsearch1:"}
    ]
    
    for engine in engines:
        search_query = f"{engine['code']}{query}"
        
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "extract_flat": False,
            "skip_download": True,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Deneniyor: {query}")
                # Arama sorgusunu doğrudan gönderiyoruz
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    
                    audio_url = entry.get('url')
                    if not audio_url:
                        continue

                    # Süreyi hesapla
                    duration_raw = entry.get('duration')
                    if duration_raw:
                        mins, secs = divmod(int(duration_raw), 60)
                        duration = f"{mins:02d}:{secs:02d}"
                    else:
                        duration = "Bilinmiyor"

                    return {
                        "title": entry.get('title', 'Bilinmeyen Parça'),
                        "webpage_url": entry.get('webpage_url', ''),
                        "file_path": audio_url, 
                        "thumbnail": entry.get('thumbnail', ''),
                        "duration": duration,
                        "source": engine['name']
                    }
            except Exception as e:
                print(f"⚠️ {engine['name']} denemesi başarısız: {str(e)[:40]}")
                continue

    # Hiçbirinde bulunamazsa en son 'Generic' bir arama dene (Doğrudan linkler için)
    raise Exception("❌ Üzgünüm, Pi Müzik bu şarkıyı hiçbir kaynakta bulamadı. Lütfen farklı kelimelerle deneyin.")
