import yt_dlp

def search_youtube(query):
    # Öncelik YouTube Müzik (Daha az koruma var), sonra YouTube, en son SoundCloud
    engines = [
        {"name": "YouTube Music", "code": "ytmsearch1:"},
        {"name": "YouTube", "code": "ytsearch1:"},
        {"name": "SoundCloud", "code": "scsearch1:"}
    ]
    
    for engine in engines:
        search_query = f"{engine['code']}{query}"
        
        # 🔥 YOUTUBE VİDEO DEĞİL SADECE SES ÇEKME VE BYPASS AYARLARI
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best", # Kesinlikle sadece ses al!
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "source_address": "0.0.0.0",
            # 🔥 EN YENİ BYPASS: YouTube'u Android Uygulaması olarak kandır.
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios"], 
                    "player_skip": ["webpage", "configs", "js"] # JS kontrollerini atla
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor (Sadece Ses): {query}")
                
                # download=False ile diske inmeden sadece canlı URL'yi al
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = info['entries'][0]
                else:
                    best_entry = info

                stream_url = best_entry.get("url")

                if not stream_url:
                    raise Exception("Canlı yayın (Stream) URL'si bulunamadı.")

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "file_path": stream_url,  # Burası URL, player.py bunu stream edecek
                    "thumbnail": best_entry.get('thumbnail', 'plugins/logo.jpg'),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} denemesi başarısız: {str(e)[:40]}")
                continue # Hata verirse bir sonraki motora (örn: SoundCloud) geçer

    return None
