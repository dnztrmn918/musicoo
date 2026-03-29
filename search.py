import yt_dlp
import os

def search_youtube(query):
    # 🚀 YOUTUBE GERİ DÖNDÜ! Öncelik YouTube'da.
    engines = [
        {"name": "YouTube", "code": "ytsearch1:"},
        {"name": "JioSaavn", "code": "jssearch1:"},
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
            "skip_download": True, 
            # 🔥 BAN AŞICI COOKIES AYARI (Klasörde cookies.txt olmalı)
            "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
            "source_address": "0.0.0.0" # IPv6 çakışmalarını önler
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] İnceleniyor: {query}")
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    best_entry = None
                    for entry in info['entries']:
                        duration_s = entry.get('duration', 0)
                        title = entry.get('title', '').lower()

                        if duration_s < 30: continue
                        if any(word in title for word in ["shorts", "teaser", "snippet", "fragman"]): continue
                        
                        best_entry = entry
                        break 
                    
                    if not best_entry: best_entry = info['entries'][0]
                else:
                    best_entry = info

                duration_raw = best_entry.get('duration')
                duration = f"{divmod(int(duration_raw), 60)[0]:02d}:{divmod(int(duration_raw), 60)[1]:02d}" if duration_raw else "Bilinmiyor"

                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "webpage_url": best_entry.get('webpage_url', ''),
                    "file_path": best_entry.get('url'), 
                    "thumbnail": best_entry.get('thumbnail', ''),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}...")
                continue

    raise Exception("❌ Aradığın kriterlerde kaliteli bir şarkı bulunamadı.")
