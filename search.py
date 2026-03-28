import yt_dlp
import os

# İndirilen şarkıların duracağı klasör
if not os.path.exists("downloads"):
    os.makedirs("downloads")

def search_youtube(query):
    # En yüksek kaliteyi sunucuya kaydetme ayarı
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(extractor)s_%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch', 
        'nocheckcertificate': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not query.startswith("http"):
            query = f"scsearch:{query}"
            
        try:
            # ARTIK SADECE LİNK BULMUYOR, SUNUCUYA İNDİRİYOR
            info = ydl.extract_info(query, download=True) 
            if 'entries' in info:
                if not info['entries']:
                    raise Exception("Aranan parça bulunamadı. 😕")
                info = info['entries'][0]
        except Exception as e:
            raise Exception(f"Arama veya İndirme hatası: {str(e)}")
            
        # İndirilen dosyanın sunucudaki tam yolu
        file_path = ydl.prepare_filename(info)
        
        return {
            'title': info.get('title', 'Bilinmeyen Şarkı'),
            'duration': info.get('duration_string', str(info.get('duration', 'Bilinmiyor'))),
            'thumbnail': info.get('thumbnail'), 
            'file_path': file_path, # URL yerine lokal dosya yolu eklendi
            'webpage_url': info.get('webpage_url', 'https://soundcloud.com')
        }
