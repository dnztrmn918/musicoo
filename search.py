import yt_dlp
import requests
import config
import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COOKIE_FILE = BASE_DIR / "cookies.txt"

def _get_audio_url(info):
    if not info: return None
    if info.get('url'): return info['url']
    if info.get('requested_formats'):
        for fmt in info['requested_formats']:
            if fmt.get('url'): return fmt['url']
    formats = info.get('formats') or []
    audio_formats = [f for f in formats if f.get('acodec') and f.get('acodec') != 'none']
    if audio_formats:
        best = max(audio_formats, key=lambda f: (f.get('abr') or f.get('tbr') or 0))
        return best.get('url')
    return None

def _search_youtube_api(query):
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    if not keys: raise Exception("❌ API anahtarı bulunamadı!")
    api_key = random.choice(keys)
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {'part': 'snippet', 'q': query, 'key': api_key, 'maxResults': 1, 'type': 'video'}
    response = requests.get(search_url, params=params)
    if response.status_code != 200: raise Exception(f"YouTube API Hatası ({response.status_code})")
    data = response.json()
    if not data.get('items'): raise Exception("🔍 Aranan parça bulunamadı.")
    item = data['items'][0]
    video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
    title = item['snippet']['title']
    thumb = item['snippet'].get('thumbnails', {}).get('high', {}).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")
    return video_url, title, thumb

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False,
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                # BURASI GÜNCELLENDİ: Global botların kullandığı istemciler
                'player_client': ['web_embedded', 'tvhtml5embedded', 'android', 'web'],
                'player_skip': ['configs', 'js'],
                'use_potoken': True # Yeni imza sistemi eklendi
            }
        }
    }

    cookiefile_path = str(COOKIE_FILE) if COOKIE_FILE.exists() else None
    if cookiefile_path:
        ydl_opts['cookiefile'] = cookiefile_path

    video_url, title, thumb = None, None, None
    if config.YOUTUBE_API_KEY:
        try: video_url, title, thumb = _search_youtube_api(query)
        except: video_url = None

    if not video_url: video_url = f"ytsearch1:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if not info: raise Exception("Ses bilgisi alınamadı.")
            if isinstance(info, dict) and info.get('entries'): info = info['entries'][0]
            raw_url = _get_audio_url(info)
            if not raw_url: raise Exception("Ses linki çıkartılamadı.")

            return {
                'title': info.get('title') or title or query,
                'thumbnail': info.get('thumbnail') or thumb or "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': raw_url,
                'webpage_url': info.get('webpage_url') or f"https://www.youtube.com/watch?v={info.get('id')}"
            }
    except Exception as e:
        err = str(e)
        if "Sign in to confirm" in err or "cookies" in err:
            raise Exception("YouTube Akış Hatası: Bot YouTube kalkanına takıldı. Lütfen taze bir cookies.txt yükleyin.")
        raise Exception(f"YouTube Akış Hatası: {err}")
