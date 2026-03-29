import yt_dlp
import os
import uuid

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
        
        # Temel yt-dlp ayarları
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": file_name,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "source_address": "0.0.0.0",
            # YouTube bot engelini aşmak için yt-dlp'yi Android gibi gösteriyoruz:
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}}
        }

        # Çerez (Cookie) dosyasını sisteme entegre ediyoruz
        if os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"
        else:
            print("⚠️ DİKKAT: 'cookies.txt' dosyası bulunamadı! YouTube indirmesi başarısız olabilir.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] İndiriliyor: {query}")
                info = ydl.extract_info(search_query, download=True)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = info['entries'][0]
                else:
                    best_entry = info

                # NoneType hatasını çözen garanti yol
                file_path = ydl.prepare_filename(best_entry)
                if not os.path.exists(file_path):
                    if "requested_downloads" in best_entry:
                        file_path = best_entry["requested_downloads"][0]["filepath"]

                if not file_path or not os.path.exists(file_path):
                    raise Exception("Dosya fiziksel olarak indirilemedi.")

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "file_path": str(file_path), 
                    "thumbnail": best_entry.get('thumbnail', ''),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}")
                continue

    raise Exception("❌ Şarkı bulunamadı veya indirilemedi.")
