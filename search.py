import yt_dlp

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch'
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
            'url': info.get('url'), # Doğrudan ses akış linki
            'webpage_url': info.get('webpage_url')
        }
