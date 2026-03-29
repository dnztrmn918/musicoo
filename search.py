import yt_dlp
import os

def search_youtube(query):
    # En stabil ve IP engeli olmayan motorlar en başta
    engines = [
        {"name": "SoundCloud", "code": "scsearch"},
        {"name": "JioSaavn", "code": "jssearch"},
        {"name": "YouTube (Piped)", "code": "ytsearch"}
    ]
    
    # Piped Proxy Listesi (YouTube için)
    piped_proxies = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.yt",
        "https://pipedapi.adminforge.de"
    ]

    for engine in engines:
        # Piped kullanılacaksa proxy döngüsü yap, yoksa tek seferlik [None]
        current_proxies = piped_proxies if engine["name"] == "YouTube (Piped)" else [None]
        
        for proxy in current_proxies:
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "default_search": engine["code"],
                "nocheckcertificate": True,
                "geo_bypass": True,
            }
            
            if proxy:
                ydl_opts["proxy"] = proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    print(f"🔍 [{engine['name']}] Aranıyor: {query}")
                    info = ydl.extract_info(query, download=False)
                    
                    if 'entries' in info and len(info['entries']) > 0:
                        info = info['entries'][0]
                        
                        # Asistanın okuyabileceği direkt ses linkini (url) döndürür
                        return {
                            "title": info.get('title', 'Bilinmeyen Parça'),
                            "webpage_url": info.get('webpage_url', ''),
                            "file_path": info.get('url'), # KRİTİK: Ses buradadır
                            "thumbnail": info.get('thumbnail', ''),
                            "source": engine['name']
                        }
                except Exception as e:
                    print(f"⚠️ {engine['name']} hatası: {str(e)[:50]}...")
                    continue

    raise Exception("❌ Hiçbir müzik platformunda şarkı bulunamadı.")
