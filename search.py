import yt_dlp
import os
import uuid

# İndirme klasörünü oluştur
if not os.path.exists("downloads"):
    os.makedirs("downloads")

def search_youtube(query):
    engines = [
        {"name": "YouTube", "code": "ytsearch1:"},
        {"name": "JioSaavn", "code": "jssearch1:"},
        {"name": "SoundCloud", "code": "scsearch1:"}
    ]
    
    for engine in engines:
        search_query = f"{engine['code']}{query}"
        
        file_name = f"downloads/{uuid.uuid4().hex}.%(ext)s"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": file_name,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
            "source_address": "0.0.0.0" 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] İndiriliyor: {query}")
                info = ydl.extract_info(search_query, download=True)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = info['entries'][0]
                else:
                    best_entry = info

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                # İndirilen dosyanın tam yolunu al (Fiziksel Dosya)
                file_path = best_entry.get("requested_downloads", [{}])[0].get("filepath", "")
                if not file_path:
                    file_path = ydl.prepare_filename(best_entry)

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "file_path": file_path, 
                    "thumbnail": best_entry.get('thumbnail', ''),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}...")
                continue

    raise Exception("❌ Aradığın kriterlerde şarkı bulunamadı veya indirilemedi.")
