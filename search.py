import yt_dlp

# 🔥 YENİ: Süre Limiti Filtresi (Maksimum 600 saniye = 10 Dakika)
def duration_filter(info, *, incomplete):
    duration = info.get('duration')
    if duration and duration > 600:
        return "Şarkı çok uzun! Lütfen 10 dakikadan kısa bir parça seçin."
    return None

def search_youtube(query):
    # Öncelik YouTube Music, sonra YouTube, en son SoundCloud
    engines = [
        {"name": "YouTube Music", "code": "ytmsearch1:"},
        {"name": "YouTube", "code": "ytsearch1:"},
        {"name": "SoundCloud", "code": "scsearch1:"}
    ]
    
    for engine in engines:
        search_query = f"{engine['code']}{query}"
        
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "source_address": "0.0.0.0",
            "cache_dir": False,
            "match_filter": duration_filter, # 🔥 10 DAKİKA SINIRINI BURADA DEVREYE SOKTUK
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios"], 
                    "player_skip": ["webpage", "configs", "js"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor (İndirmeden Anında Çalınacak): {query}")
                
                # 🔥 İNDİRMEYİ KAPATTIK (download=False)
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = info['entries'][0]
                else:
                    best_entry = info

                stream_url = best_entry.get("url")

                if not stream_url:
                    raise Exception("Canlı yayın URL'si bulunamadı.")

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "file_path": stream_url, # Artık diske inen dosya değil, doğrudan internet adresi!
                    "thumbnail": best_entry.get('thumbnail', 'plugins/logo.jpg'),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                # 10 dakikadan uzunsa diğer motorlara bakmadan direkt reddet
                if "Şarkı çok uzun" in str(e):
                    print(f"⚠️ {engine['name']} Reddedildi: Şarkı 10 dakikadan uzun.")
                    raise Exception("10 dakikadan uzun parçalar açılamaz!")
                
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}")
                continue

    return None
