import yt_dlp
import os

# İndirilen dosyaların tutulacağı klasör
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def search_youtube(query):
    # IP engeli olmayan en sağlam motorlar
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
            # --- DEĞİŞEN KRİTİK AYARLAR ---
            "skip_download": False, # ARTIK SUNUCUYA FİZİKSEL OLARAK İNDİRİYORUZ
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s_%(extractor)s.%(ext)s"), # İndirilecek klasör ve dosya adı formatı
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor ve İndiriliyor: {query}")
                info = ydl.extract_info(search_query, download=True) # İndirme işlemini tetikliyoruz
                
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                else:
                    entry = info
                    
                # İNDİRİLEN FİZİKSEL DOSYANIN SUNUCUDAKİ YERİNİ BULUYORUZ
                file_path = ydl.prepare_filename(entry)

                if not file_path or not os.path.exists(file_path):
                    continue

                # SÜRE HESAPLAMA (Örn: 03:45)
                duration_raw = entry.get('duration')
                if duration_raw:
                    mins, secs = divmod(int(duration_raw), 60)
                    duration = f"{mins:02d}:{secs:02d}"
                else:
                    duration = "Bilinmiyor"

                return {
                    "title": entry.get('title', 'Bilinmeyen Parça'),
                    "webpage_url": entry.get('webpage_url', ''),
                    "file_path": file_path,  # ARTIK LİNK DEĞİL, SUNUCUDAKİ DOSYA YOLU (Örn: downloads/123_soundcloud.m4a)
                    "thumbnail": entry.get('thumbnail', ''),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}...")
                continue

    raise Exception("❌ Üzgünüm, aradığın şarkıyı bulamadım veya sunucuya indiremedim.")
