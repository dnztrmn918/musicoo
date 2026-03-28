import yt_dlp
import requests
import config
import random

def search_youtube(query):
    # 1. API KEY HAVUZU
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    if not keys:
        raise Exception("❌ API anahtarı bulunamadı!")

    api_key = random.choice(keys)

    # 2. YOUTUBE DATA API V3 İLE ARAMA YAP
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'key': api_key,
        'maxResults': 1,
        'type': 'video'
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        raise Exception(f"YouTube API Hatası ({response.status_code})")
    
    data = response.json()
    if not data.get('items'):
        raise Exception("🔍 Aranan parça bulunamadı.")
    
    video_id = data['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    title = data['items'][0]['snippet']['title']
    
    thumbnails = data['items'][0]['snippet'].get('thumbnails', {})
    thumb = thumbnails.get('high', thumbnails.get('default', {})).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")

    # 3. YT-DLP: SAF ANDROID İSTEMCİSİ VE SIFIR ÖNBELLEK
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        # KRİTİK 1: Önbelleği kapatıyoruz! Her şarkıda yeni kimlik alacak.
        'cachedir': False, 
        # KRİTİK 2: Çerez yok, sadece Android cihaz taklidi var. JS kontrolleri kapalı.
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'player_skip': ['webpage', 'configs', 'js']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Linki güvenli şekilde çekiyoruz
            raw_url = info.get('url') or (info.get('requested_formats') and info['requested_formats'][0].get('url'))
            
            if not raw_url:
                raise Exception("Ses linki çıkartılamadı, format desteklenmiyor olabilir.")
                
            return {
                'title': title,
                'thumbnail': thumb,
                'file_path': raw_url,
                'webpage_url': video_url
            }
    except Exception as e:
        # Hata mesajında artık cookies.txt aramayacak
        raise Exception(f"YouTube Akış Hatası: {str(e)}")
