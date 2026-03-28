import yt_dlp
import requests
import config

def search_youtube(query):
    api_key = config.YOUTUBE_API_KEY
    if not api_key:
        raise Exception("❌ API1 anahtarı bulunamadı! Koyeb ayarlarını kontrol et.")

    # 1. ADIM: YouTube API ile Arama Yap (Hızlı ve Kesin)
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
        raise Exception(f"YouTube API Hatası: {response.status_code}")
    
    data = response.json()
    if not data.get('items'):
        raise Exception("🔍 Aranan parça bulunamadı.")
    
    video_id = data['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    title = data['items'][0]['snippet']['title']
    thumb = data['items'][0]['snippet']['thumbnails']['high']['url']

    # 2. ADIM: yt-dlp ile Ses Akış Linkini (Direct Link) Al
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        raw_url = info['url'] # İndirmeden direkt çalınacak link

    return {
        'title': title,
        'thumbnail': thumb,
        'file_path': raw_url, # player.py indirme beklediği için ismini bozmadım
        'webpage_url': video_url
    }
