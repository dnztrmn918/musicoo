import yt_dlp

def search_youtube(query):
    # Çerez dosyasına, bot ayarlarına GEREK YOK!
    # Sadece SoundCloud üzerinden temiz ve hızlı arama yapacağız.
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch', # SİHİRLİ KELİME: YouTube yerine SoundCloud'da ara
        'nocheckcertificate': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not query.startswith("http"):
            query = f"scsearch:{query}" # scsearch = SoundCloud Search
            
        info = ydl.extract_info(query, download=False)
        
        if 'entries' in info:
            info = info['entries'][0]
            
        return {
            'title': info.get('title'),
            'duration': info.get('duration_string', 'Bilinmiyor'),
            'thumbnail': info.get('thumbnail'),
            'url': info.get('url'), # Doğrudan ses dosyası
            'webpage_url': info.get('webpage_url', '#')
        }
