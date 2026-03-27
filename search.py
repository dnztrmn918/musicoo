import yt_dlp

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'auto',  # Sadece SoundCloud değil, her yeri arar
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt' # Botun engellenmemesi için eklenen kritik satır
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
            'duration': info.get('duration_string', str(info.get('duration', 'Bilinmiyor'))),
            'thumbnail': info.get('thumbnail'), 
            'url': info.get('url'), 
            'webpage_url': info.get('webpage_url', 'https://youtube.com')
        }
