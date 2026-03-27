import yt_dlp

def search_youtube(query):
    # Çerez dosyasına GEREK YOK!
    # Youtube'u atlıyor, SoundCloud'da arıyoruz.
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch', # SİHİRLİ KİŞİM: Youtube yerine SoundCloud
        'nocheckcertificate': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not query.startswith("http"):
            query = f"scsearch:{query}"
            
        info = ydl.extract_info(query, download=False)
        
        if 'entries' in info:
            info = info['entries'][0]
            
        return {
            'title': info.get('title'),
            'duration': info.get('duration_string', 'Bilinmiyor'),
            'thumbnail': info.get('thumbnail'),
            'url': info.get('url'), # Oynatılacak ham ses dosyası
            'webpage_url': info.get('webpage_url', 'https://soundcloud.com')
        }
