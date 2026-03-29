import yt_dlp
import os

def search_youtube(query):
    # YouTube tamamen kaldırıldı, sadece IP engeli olmayan motorlar kaldı.
    engines = [
        {"name": "SoundCloud", "code": "scsearch"},
        {"name": "JioSaavn", "code": "jssearch"}
    ]
    
    for engine in engines:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "default_search": engine["code"],
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor: {query}")
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                    
                    # Asistanın (PyTgCalls) okuyabileceği doğrudan ses linki
                    audio_url = info.get('url')
                    
                    # Eğer url boşsa veya geçerli değilse bir sonrakine geç
                    if not audio_url:
                        continue

                    return {
                        "title": info.get('title', 'Bilinmeyen Parça'),
                        "webpage_url": info.get('webpage_url', ''),
                        "file_path": audio_url, 
                        "thumbnail": info.get('thumbnail', ''),
                        "source": engine['name']
                    }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:50]}...")
                continue

    raise Exception("❌ SoundCloud ve Saavn üzerinde şarkı bulunamadı.")
