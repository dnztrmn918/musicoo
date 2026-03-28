import yt_dlp
import requests
import config
import random
import os

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

    # 3. YT-DLP: GÜNCEL VE ÇEREZ DESTEKLİ AYARLAR
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False, 
        # Taze cookies.txt dosyasını burada devreye sokuyoruz
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'extractor_args': {
            'youtube': {
                # Farklı cihaz taklitleriyle YouTube kalkanlarını aşıyoruz
                'player_client': ['android', 'web', 'ios'],
                'player_skip': ['configs', 'js']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False diyerek sadece linki çekiyoruz
            info = ydl.extract_info(video_url, download=False)
            
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
        raise Exception(f"YouTube Akış Hatası: {str(e)}")
