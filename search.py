import yt_dlp
import os
import uuid

if not os.path.exists("downloads"):
    os.makedirs("downloads")

def search_youtube(query):
    # Öncelik YouTube Müzik, sonra YouTube, en son SoundCloud
    engines = [
        {"name": "YouTube Music", "code": "ytmsearch1:"},
        {"name": "YouTube", "code": "ytsearch1:"},
        {"name": "SoundCloud", "code": "scsearch1:"}
    ]
    
    for engine in engines:
        search_query = f"{engine['code']}{query}"
        file_name = f"downloads/{uuid.uuid4().hex}.%(ext)s"
        
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": file_name,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "source_address": "0.0.0.0",
            "cache_dir": False,  # 🔥 RAM ŞİŞMESİNİ VE BAĞLANTI KOPMASINI ENGELLEYEN SİHİRLİ AYAR
            # YouTube Bypass
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios"], 
                    "player_skip": ["webpage", "configs", "js"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor ve İndiriliyor: {query}")
                
                # 🔥 LİNKLER ÖLMESİN DİYE İNDİRMEYİ GERİ AÇTIK (download=True)
                info = ydl.extract_info(search_query, download=True)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = info['entries'][0]
                else:
                    best_entry = info

                file_path = ydl.prepare_filename(best_entry)
                if not os.path.exists(file_path):
                    if "requested_downloads" in best_entry:
                        file_path = best_entry["requested_downloads"][0]["filepath"]

                if not file_path or not os.path.exists(file_path):
                    raise Exception("Fiziksel dosya bulunamadı.")

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "file_path": str(file_path),
                    "thumbnail": best_entry.get('thumbnail', 'plugins/logo.jpg'),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}")
                continue

    return None
