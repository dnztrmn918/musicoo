import yt_dlp

def search_youtube(query):
    # Çok kısıtlamıyoruz, bestaudio ile en iyi kaliteyi çekiyoruz
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch', 
        'nocheckcertificate': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not query.startswith("http"):
            query = f"scsearch:{query}"
            
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                if not info['entries']:
                    raise Exception("Aranan parça bulunamadı. 😕")
                info = info['entries'][0]
        except Exception as e:
            raise Exception(f"Arama hatası: {str(e)}")
            
        return {
            'title': info.get('title', 'Bilinmeyen Şarkı'),
            'duration': info.get('duration_string', 'Bilinmiyor'),
            'thumbnail': info.get('thumbnail'), 
            'url': info.get('url'), 
            'webpage_url': info.get('webpage_url', 'https://soundcloud.com')
        }
