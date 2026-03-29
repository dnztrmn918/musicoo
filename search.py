import yt_dlp
import requests
import config
import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COOKIE_FILE = BASE_DIR / "cookies.txt"

# ──────────────────────────────────────────
# ALTERNATİF MOTORLAR (DEEZER & SOUNDCLOUD)
# ──────────────────────────────────────────
def search_deezer(query):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True, 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"dzsearch1:{query}", download=False)
            if not info or not info.get('entries'): return None
            info = info['entries'][0]
            url = info.get('url') or (info.get('formats') and info['formats'][0].get('url'))
            if not url: return None
            return {
                'title': info.get('title') or query,
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
            url = info.get('url') or (info.get('formats') and info['formats'][0].get('url'))
            if not url: return None
            return {
                'title': info.get('title') or query,
                'thumbnail': info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': url,
                'webpage_url': info.get('webpage_url') or "https://soundcloud.com/"
            }
    except: return None

# ──────────────────────────────────────────
# YOUTUBE API ARAMA MOTORU
# ──────────────────────────────────────────
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
    return f"https://www.youtube.com/watch?v={item['id']['videoId']}", item['snippet']['title'], item['snippet'].get('thumbnails', {}).get('high', {}).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")

# ──────────────────────────────────────────
# ANA ARAMA VE İNDİRME MOTORU (YOUTUBE)
# ──────────────────────────────────────────
def search_youtube(query):
    # KRİTİK DEĞİŞİKLİK: Artık sadece link almıyoruz, dosyayı sunucuya indiriyoruz.
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False,
        'noplaylist': True,
        'outtmpl': '%(id)s.%(ext)s', # İndirilen dosyanın isim formatı
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios'],
                'player_skip': ['configs', 'js']
            }
        }
    }

    if COOKIE_FILE.exists():
        ydl_opts['cookiefile'] = str(COOKIE_FILE)

    video_url, title, thumb = None, None, None
    if config.YOUTUBE_API_KEY:
        try: video_url, title, thumb = _search_youtube_api(query)
        except: video_url = f"ytsearch1:{query}"
    else: 
        video_url = f"ytsearch1:{query}"

    last_err = None
    for attempt in range(3):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # KRİTİK NOKTA: download=True yapıldı. FFmpeg çökmeyecek!
                info = ydl.extract_info(video_url, download=True)
                
                if not info: raise Exception("Ses bilgisi alınamadı.")
                if isinstance(info, dict) and info.get('entries'): info = info['entries'][0]
                
                # 15 dakika sınırı
                if info.get('duration', 0) > 15 * 60: raise Exception("15 dakikadan uzun")
                
                # İndirilen dosyanın tam yolunu alıyoruz
                file_path = ydl.prepare_filename(info)

                return {
                    'title': info.get('title') or title or query,
                    'thumbnail': info.get('thumbnail') or thumb or "https://telegra.ph/file/69204068595f57731936c.jpg",
                    'file_path': file_path, # Yerel dosya yolu (örn: XyZ123.webm)
                    'webpage_url': info.get('webpage_url') or video_url
                }
        except Exception as e:
            last_err = str(e)
            
            # Eğer çerez/bot engeline takılırsa anında alternatiflere geç (Node.js kurtarıcısı)
            if any(x in last_err.lower() for x in ["sign in", "confirm you're not a bot", "cookies"]):
                deezer = search_deezer(query)
                if deezer: return deezer
                sc = search_soundcloud(query)
                if sc: return sc
                break
                
            # Geçici bağlantı kopmalarında tekrar dene
            if any(x in last_err.lower() for x in ["network", "timeout", "try again", "temporarily"]):
                continue
            break

    raise Exception(f"❌ Müzik Motoru Hatası: {last_err}")
