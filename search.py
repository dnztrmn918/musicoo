import yt_dlp

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'cookiefile': 'cookies.txt',
        'nocheckcertificate': True,
        # BÜTÜN SİHİR BURADA: Web arayüzünü tamamen atla, sadece mobil cihaz gibi davran
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'], # Sadece Android ve iOS
                'player_skip': ['webpage', 'default'] # Bot kontrolünün yapıldığı web sayfasını es geç
            }
        },
        # YouTube'u normal bir kullanıcı olduğumuza inandırmak için sahte kimlik:
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
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
            'url': info.get('url'), # Bu, doğrudan ses dosyasıdır
            'webpage_url': info.get('webpage_url')
        }
