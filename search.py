import yt_dlp
import os

def search_youtube(query):
    # IP engeli olmayan en hızlı motorlar
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
            # Ekstra stabilite ayarları
            "cachedir": False,
            "youtube_include_dash_manifest": False,
            "allowed_extractors": ["soundcloud", "saavn", "generic"]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor: {query}")
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                    
                    audio_url = info.get('url')
                    if not audio_url:
                        continue

                    # SÜRE HESAPLAMA (Saniye cinsinden gelen veriyi MM:SS yapar)
                    duration_raw = info.get('duration')
                    if duration_raw:
                        mins, secs = divmod(int(duration_raw), 60)
                        duration = f"{mins:02d}:{secs:02d}"
                    else:
                        duration = "Canlı/Bilinmiyor"

                    return {
                        "title": info.get('title', 'Bilinmeyen Parça'),
                        "webpage_url": info.get('webpage_url', ''),
                        "file_path": audio_url, 
                        "thumbnail": info.get('thumbnail', ''),
                        "duration": duration, # player.py'nin beklediği alan
                        "source": engine['name']
                    }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:50]}...")
                continue

    raise Exception("❌ SoundCloud ve Saavn üzerinde şarkı bulunamadı.")
