import yt_dlp
import requests
import config
import random
import os
from pathlib import Path

# Dosya yolları için profesyonel yapı
BASE_DIR = Path(__file__).resolve().parent

def _get_audio_url(info):
    """YouTube formatları arasından en kaliteli ses linkini ayıklar."""
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
    """YouTube Data API v3 kullanarak hızlı arama yapar."""
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
    return f"https://www.youtube.com/watch?v={item['id']['videoId']}", item['snippet']['title'], item['snippet'].get('thumbnails', {}).get('high', {}).get('url', "")

def search_youtube(query):
    # GLOBAL OAUTH2 VE BYPASS AYARLARI
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'geo_bypass': True,
        'cachedir': False,
        'noplaylist': True
