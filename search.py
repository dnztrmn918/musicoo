import yt_dlp

def search_youtube(query):
    # Öncelik tamamen SoundCloud'a verildi
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch',  # SoundCloud araması
        'nocheckcertificate': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Eğer kullanıcı direkt link atmadıysa (isim yazdıysa) SoundCloud'da ara
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
            'duration': info.get('duration_string', str(info.get('duration', 'Bilinmiyor'))),
            'thumbnail': info.get('thumbnail'), # SoundCloud kapağı
            'url': info.get('url'), # Ham ses dosyası
            'webpage_url': info.get('webpage_url', 'https://soundcloud.com')
        }
