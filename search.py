import yt_dlp
import requests
import config
import random
import os

def search_youtube(query):
    # 1. API İLE ARAMA (Quota Dostu)
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    api_key = random.choice(keys)
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {'part': 'snippet', 'q': query, 'key': api_key, 'maxResults': 1, 'type': 'video'}
    
    res = requests.get(search_url, params=params).json()
    video_id = res['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # 2. GLOBAL BYPASS AYARLARI
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        # ÖNEMLİ: YouTube'u "Gömülü Oynatıcı" (Embedded) olduğuna ikna ediyoruz
        'extractor_args': {
            'youtube': {
                'player_client': ['web_embedded', 'tvhtml5embedded', 'android'],
                'player_skip': ['configs', 'js'],
                # Global botların kullandığı 'imza' sistemi
                'use_potoken': True,
            }
        },
        # YouTube'u şaşırtmak için farklı bir User-Agent
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # En temiz ses linkini seç
            raw_url = info.get('url') or (info.get('requested_formats') and info['requested_formats'][0].get('url'))
            
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'file_path': raw_url,
                'webpage_url': video_url
            }
    except Exception as e:
        # Eğer hala hata verirse, son çare 'OAUTH' sistemini denemesi için mesaj basıyoruz
        raise Exception(f"YouTube Kalkanı Aşılamadı. Lütfen yt-dlp sürümünü kontrol et veya OAuth kullan. Detay: {str(e)}")
