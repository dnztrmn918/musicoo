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

def search_deezer(query):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True, 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"dzsearch1:{query}", download=False)
            if not info or not info.get('entries'): return None
            info = info['entries'][0]
            url = _get_audio_url(info)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': url,
                'webpage_url': info.get('webpage_url') or "https://www.deezer.com/"
            }
    except: return None

def search_soundcloud(query):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True, 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch1:{query}", download=False)
            if not info or not info.get('entries'): return None
            info = info['entries'][0]
            url = _get_audio_url(info)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': url,
                'webpage_url': info.get('webpage_url') or "https://soundcloud.com/"
            }
    except: return None

def _search_youtube_api(query):
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    if not keys: raise Exception("❌ API anahtarı bulunamadı!")
    api_key = random.choice(keys)
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {'part': 'snippet', 'q': query, 'key': api_key, 'maxResults': 1, 'type': 'video'}
    response = requests.get(search_url, params=params)
    data = response.json()
    if not data.get('items'): raise Exception("🔍 Aranan parça bulunamadı.")
    item = data['items'][0]
    return f"https://www.youtube.com/watch?v={item['id']['videoId']}", item['snippet']['title'], item['snippet'].get('thumbnails', {}).get('high', {}).get('url', "")

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
        'source_address': '0.0.0.0', 'geo_bypass': True, 'cachedir': False, 'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web', 'ios'], 'player_skip': ['configs', 'js']}}
    }
    if COOKIE_FILE.exists(): ydl_opts['cookiefile'] = str(COOKIE_FILE)

    video_url, title, thumb = None, None, None
    if config.YOUTUBE_API_KEY:
        try: video_url, title, thumb = _search_youtube_api(query)
        except: video_url = f"ytsearch1:{query}"
    else: video_url = f"ytsearch1:{query}"

    last_err = None
    for attempt in range(3):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if isinstance(info, dict) and info.get('entries'): info = info['entries'][0]
                
                # Süre kontrolü
                if info.get('duration', 0) > 15 * 60: raise Exception("15 dakikadan uzun")
                
                raw_url = _get_audio_url(info)
                if not raw_url: raise Exception("link çıkartılamadı")

                return {
                    'title': info.get('title') or title or query,
                    'thumbnail': info.get('thumbnail') or thumb or "https://telegra.ph/file/69204068595f57731936c.jpg",
                    'file_path': raw_url,
                    'webpage_url': info.get('webpage_url') or video_url
                }
        except Exception as e:
            last_err = str(e)
            if any(x in last_err.lower() for x in ["sign in", "confirm you're not a bot", "cookies"]):
                # YouTube kalkanı! Hemen fallback'leri dene
                deezer = search_deezer(query)
                if deezer: return deezer
                sc = search_soundcloud(query)
                if sc: return sc
            if any(x in last_err.lower() for x in ["network", "timeout", "try again"]): continue
            break

    raise Exception(f"❌ Müzik Motoru Hatası: {last_err}")
