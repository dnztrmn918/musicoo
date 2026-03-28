import yt_dlp
import requests
import config
import random

def search_youtube(query):
    # 10 Key Havuzu Mantığı: config içindeki virgüllü string'i listeye çeviriyoruz
    # Koyeb'de YT_KEYS olarak girdiğin tüm anahtarları deneyecektir.
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    
    if not keys:
        raise Exception("❌ API anahtarı bulunamadı! Koyeb YT_KEYS ayarını kontrol et.")

    # Havuzdan rastgele bir key seçerek kotayı dağıtıyoruz
    api_key = random.choice(keys)

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
        # Eğer bu key patlamışsa veya hata vermişse bilgi ver
        raise Exception(f"YouTube API Hatası ({response.status_code}): Lütfen API keylerinizi kontrol edin.")
    
    data = response.json()
    if not data.get('items'):
        raise Exception("🔍 Aranan parça bulunamadı.")
    
    video_id = data['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    title = data['items'][0]['snippet']['title']
    
    # Thumbnail güvenliği
    thumbnails = data['items'][0]['snippet'].get('thumbnails', {})
    thumb = thumbnails.get('high', thumbnails.get('default', {})).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")

    # 2. ADIM: yt-dlp ile Ses Akış Linkini (Direct Link) Al
    # YouTube'un "Bot musun?" engelini (Sign in hatası) aşmak için ayarlar eklendi.
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # KRİTİK AYARLAR: YouTube engelini aşmak için tarayıcı gibi davranıyoruz
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'geo_bypass': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            raw_url = info['url'] # İndirmeden direkt çalınacak link
    except Exception as e:
        # Eğer hala çerez hatası verirse kullanıcıya detaylı hata dön
        raise Exception(f"YouTube Akış Hatası: {str(e)}")

    return {
        'title': title,
        'thumbnail': thumb,
        'file_path': raw_url, # player.py uyumu için isim korundu
        'webpage_url': video_url
    }
