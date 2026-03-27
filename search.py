import yt_dlp
import os

def search_youtube(query):
    # Sunucudaki tam dosya yolunu buluyoruz (Örn: /app/cookies.txt)
    cookie_path = os.path.abspath("cookies.txt")
    
    # KONSOLA YAZDIR: Dosya gerçekten orada mı?
    if os.path.exists(cookie_path):
        print(f"✅ Çerez dosyası BURADA: {cookie_path}")
    else:
        print(f"❌ DİKKAT: Çerez dosyası BULUNAMADI! Aranan yer: {cookie_path}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'cookiefile': cookie_path, # Artık tahmini değil, tam adresi veriyoruz
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'player_skip': ['webpage', 'default']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not query.startswith("http"):
            query = f"ytsearch:{query}"
            
        info = ydl.extract_info(query, download=False)
        
        if 'entries' in info:
            info = info['entries'][0]
            
        return {
            'title': info.get('title'),
            'duration': info.get('duration_string', 'Bilinmiyor'),
            'thumbnail': info.get('thumbnail'),
            'url': info.get('url'),
            'webpage_url': info.get('webpage_url')
        }
