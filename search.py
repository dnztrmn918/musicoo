import yt_dlp
import requests
import config
import random

# Koyeb'den virgülle ayrılmış anahtarları alıyoruz
YT_KEYS_LIST = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]

def search_youtube(query):
    if not YT_KEYS_LIST:
        raise Exception("❌ API anahtarı bulunamadı! Koyeb YT_KEYS kontrol et.")

    # Rastgele bir key seçerek kotayı dağıtıyoruz
    api_key = random.choice(YT_KEYS_LIST)

    # 1. ADIM: YouTube API Arama
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
        # Eğer bu key patlamışsa listeden bir başkasını dene (basit hata yönetimi)
        raise Exception(f"YouTube API Hatası: {response.status_code}. Diğer keyleri kontrol edin.")
    
    data = response.json()
    if not data.get('items'):
        raise Exception("🔍 Aranan parça bulunamadı.")
    
    item = data['items'][0]
    video_id = item['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    title = item['snippet']['title']
    
    # Thumbnail güvenliği: Eğer yüksek kalite yoksa standart olanı al
    thumbnails = item['snippet'].get('thumbnails', {})
    thumb = thumbnails.get('high', thumbnails.get('default', {})).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")

    # 2. ADIM: yt-dlp ile Akış Linki
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        raw_url = info['url'] 

    return {
        'title': title,
        'thumbnail': thumb,
        'file_path': raw_url, # player.py için URL'yi yol olarak veriyoruz
        'webpage_url': video_url
    }
