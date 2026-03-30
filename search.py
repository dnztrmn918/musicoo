import yt_dlp

def search_youtube(query):
    # SoundCloud ve JioSaavn'ı yedek olarak bıraktım ama ana hedef YouTube
    engines = [
        {"name": "YouTube", "code": "ytsearch1:"},
        {"name": "SoundCloud", "code": "scsearch1:"}
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
            "source_address": "0.0.0.0",
            # Usta işi Bypass: YouTube bot korumasını delen mobil ve TV istemcileri
            "extractor_args": {"youtube": {"player_client": ["android", "ios", "tv"]}}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor (İndirmeden Stream Edilecek): {query}")
                
                # 🔥 DİKKAT: download=False yapıldı! Artık diske inmeyecek.
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = info['entries'][0]
                else:
                    best_entry = info

                # İnen fiziksel dosya yerine şarkının asıl medya linkini alıyoruz
                stream_url = best_entry.get("url")

                if not stream_url:
                    raise Exception("Medya yayın linki bulunamadı.")

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "file_path": stream_url, # player.py hata vermesin diye adı aynı kaldı ama artık bu bir URL!
                    "thumbnail": best_entry.get('thumbnail', 'plugins/logo.jpg'),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} Bypass edilemedi veya bulunamadı: {str(e)[:40]}")
                continue

    return None
