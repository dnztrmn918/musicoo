import yt_dlp
import requests
import config
import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COOKIE_FILE = BASE_DIR / "cookies.txt"

# Deezer ve SoundCloud fallback fonksiyonları
def search_deezer(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"dzsearch1:{query}", download=False)
            if not info or not info.get('entries'):
                raise Exception("Deezer'da parça bulunamadı.")
            info = info['entries'][0]
            url = info.get('url') or (info.get('formats') and info['formats'][0].get('url'))
            if not url:
                raise Exception("Deezer ses linki çıkarılamadı.")
            return {
                'title': info.get('title') or query,
                'thumbnail': info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': url,
                'webpage_url': info.get('webpage_url') or info.get('original_url') or "https://www.deezer.com/"
            }
    except Exception as e:
        raise Exception(f"Deezer Akış Hatası: {e}")

def search_soundcloud(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch1:{query}", download=False)
            if not info or not info.get('entries'):
                raise Exception("SoundCloud'da parça bulunamadı.")
            info = info['entries'][0]
            url = info.get('url') or (info.get('formats') and info['formats'][0].get('url'))
            if not url:
                raise Exception("SoundCloud ses linki çıkarılamadı.")
            return {
                'title': info.get('title') or query,
                'thumbnail': info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': url,
                'webpage_url': info.get('webpage_url') or info.get('original_url') or "https://soundcloud.com/"
            }
    except Exception as e:
        raise Exception(f"SoundCloud Akış Hatası: {e}")
import yt_dlp
import requests
import config
import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COOKIE_FILE = BASE_DIR / "cookies.txt"


def _get_audio_url(info):
    if not info:
        return None

    if info.get('url'):
        return info['url']

    if info.get('requested_formats'):
        for fmt in info['requested_formats']:
            if fmt.get('url'):
                return fmt['url']

    formats = info.get('formats') or []
    audio_formats = [f for f in formats if f.get('acodec') and f.get('acodec') != 'none']
    if audio_formats:
        best = max(audio_formats, key=lambda f: (f.get('abr') or f.get('tbr') or 0))
        return best.get('url')

    return None


def _search_youtube_api(query):
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    if not keys:
        raise Exception("❌ API anahtarı bulunamadı!")

    api_key = random.choice(keys)
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

    item = data['items'][0]
    video_id = item['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    title = item['snippet']['title']
    thumbnails = item['snippet'].get('thumbnails', {})
    thumb = thumbnails.get('high', thumbnails.get('default', {})).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")

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
                'player_client': ['android', 'web', 'ios'],
                'player_skip': ['configs', 'js']
            }
        }
    }

    cookiefile_path = str(COOKIE_FILE) if COOKIE_FILE.exists() else None
    if cookiefile_path:
        ydl_opts['cookiefile'] = cookiefile_path

    video_url = None
    title = None
    thumb = None

    if config.YOUTUBE_API_KEY:
        try:
            video_url, title, thumb = _search_youtube_api(query)
        except Exception:
            video_url = None

    if not video_url:
        video_url = f"ytsearch1:{query}"

    # Retry logic
    last_err = None
    for attempt in range(3):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    raise Exception("Ses bilgisi alınamadı.")

                if isinstance(info, dict) and info.get('entries'):
                    info = info['entries'][0]

                # Süre kontrolü (ör: 15 dakikadan uzun şarkı engelle)
                duration = info.get('duration')
                if duration and duration > 15 * 60:
                    raise Exception("Bu şarkı 15 dakikadan uzun, oynatılamaz.")

                raw_url = _get_audio_url(info)
                if not raw_url:
                    raise Exception("Ses linki çıkartılamadı, format desteklenmiyor olabilir.")

                return {
                    'title': info.get('title') or title or query,
                    'thumbnail': info.get('thumbnail') or thumb or "https://telegra.ph/file/69204068595f57731936c.jpg",
                    'file_path': raw_url,
                    'webpage_url': info.get('webpage_url') or f"https://www.youtube.com/watch?v={info.get('id')}"
                }
        except Exception as e:
            last_err = str(e)
            # Bazı hatalarda tekrar denemek mantıklı (ör: network, yt-dlp geçici hata)
            if any(x in last_err.lower() for x in ["network", "timeout", "try again", "temporarily unavailable", "yt-dlp"]):
                continue
            # Eğer cookies hatası varsa Deezer ve SoundCloud fallback
            if "Sign in to confirm" in last_err or "cookies" in last_err:
                try:
                    return search_deezer(query)
                except Exception:
                    pass
                try:
                    return search_soundcloud(query)
                except Exception:
                    pass
            break

    # Hata türüne göre açıklama
    if last_err:
        if "Sign in to confirm" in last_err or "cookies" in last_err:
            raise Exception("YouTube ve alternatif kaynaklarda uygun sonuç bulunamadı. Lütfen farklı bir şarkı deneyin veya cookies.txt dosyanızı güncelleyin.")
        if "15 dakikadan uzun" in last_err:
            raise Exception("YouTube Akış Hatası: Bu şarkı 15 dakikadan uzun olduğu için oynatılamaz.")
        if "format desteklenmiyor" in last_err:
            raise Exception("YouTube Akış Hatası: Ses formatı desteklenmiyor veya link çıkarılamadı.")
        if "bulunamadı" in last_err:
            raise Exception("YouTube Akış Hatası: Aranan parça bulunamadı.")
        raise Exception(f"YouTube Akış Hatası: {last_err}")
