import yt_dlp
import os

def search_youtube(query):
    # Piped API Proxy Listesi (Biri çalışmazsa diğeri denenir)
    piped_proxies = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.yt",
        "https://pipedapi.moomoo.me"
    ]
    
    # Motorlar: Önce YouTube (Piped ile), sonra SoundCloud
    engines = ["ytsearch", "scsearch"]
    
    for engine in engines:
        for proxy in (piped_proxies if engine == "ytsearch" else [None]):
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "default_search": engine,
                "nocheckcertificate": True,
                "geo_bypass": True,
            }
            
            if proxy:
                ydl_opts["proxy"] = proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    print(f"🔍 [{engine}] {'Proxy: ' + proxy if proxy else ''} üzerinden aranıyor: {query}")
                    info = ydl.extract_info(query, download=False)
                    
                    if 'entries' in info and len(info['entries']) > 0:
                        info = info['entries'][0]
                        return {
                            "title": info.get('title', 'Bilinmeyen Parça'),
                            "webpage_url": info.get('webpage_url', ''),
                            "file_path": info.get('url'),
                            "thumbnail": info.get('thumbnail', ''),
                            "source": engine
                        }
                except Exception as e:
                    print(f"⚠️ {engine} denemesi başarısız: {str(e)}")
                    continue # Diğer proxy veya motoru dene

    raise Exception("❌ Piped ve SoundCloud kaynakları tükendi, şarkı bulunamadı.")
