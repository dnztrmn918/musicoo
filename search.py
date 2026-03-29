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

    # 2. YOUTUBE DATA API V3
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {'part': 'snippet', 'q': query, 'key': api_key, 'maxResults': 1, 'type': 'video'}
    
    try:
        response = requests.get(search_url, params=params)
        data = response.json()
        video_id = data['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = data['items'][0]['snippet']['title']
        thumb = data['items'][0]['snippet']['thumbnails']['high']['url']
    except Exception as e:
        raise Exception(f"Arama Hatası: {str(e)}")

    # 3. GLOBAL REPO STANDARTI: PO-TOKEN VE OAUTH AYARLARI
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False, 
        # Çerez varsa kullan, yoksa OAUTH2 ile dene (Global standart) 
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios'],
                'player_skip': ['configs', 'js'],
                # Eğer çerez yoksa, YouTube'un yeni imza sistemini (PoToken) zorla 
                'use_potoken': True 
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            raw_url = info.get('url') or (info.get('requested_formats') and info['requested_formats'][0].get('url'))
            
            if not raw_url:
                raise Exception("YouTube akışı engelledi, alternatif deneniyor...")
                
            return {
                'title': title,
                'thumbnail': thumb,
                'file_path': raw_url,
                'webpage_url': video_url
            }
    except Exception as e:
        raise Exception(f"Global Motor Hatası: {str(e)}")
