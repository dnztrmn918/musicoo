import yt_dlp
import os

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
            "skip_download": True,
            # --- SES HATASINI ÇÖZEN KRİTİK AYARLAR ---
            "protocol": "https", # Güvenli protokol zorla
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] Aranıyor: {query}")
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    
                    # ASİSTANIN OKUYABİLECEĞİ SES LİNKİ
                    audio_url = entry.get('url')
                    if not audio_url:
                        continue

                    # SÜRE HESAPLAMA (Örn: 03:45)
                    duration_raw = entry.get('duration')
                    if duration_raw:
                        mins, secs = divmod(int(duration_raw), 60)
                        duration = f"{mins:02d}:{secs:02d}"
                    else:
                        duration = "Canlı/Bilinmiyor"

                    return {
                        "title": entry.get('title', 'Bilinmeyen Parça'),
                        "webpage_url": entry.get('webpage_url', ''),
                        "file_path": audio_url, 
                        "thumbnail": entry.get('thumbnail', ''),
                        "duration": duration,
                        "source": engine['name']
                    }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}...")
                continue

    raise Exception("❌ Üzgünüm, aradığın şarkıyı hiçbir kaynakta (SC/Saavn/Bandcamp) bulamadım.")
