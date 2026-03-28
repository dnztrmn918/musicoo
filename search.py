import yt_dlp
import requests
import config
import random

def search_youtube(query):
    # 1. ADIM: API KEY HAVUZUNU HAZIRLA
    # Koyeb'deki YT_KEYS değişkeninden anahtarları virgülle ayırarak listeye çevirir.
    keys = [k.strip() for k in config.YOUTUBE_API_KEY.split(",") if k.strip()]
    
    if not keys:
        raise Exception("❌ API anahtarı bulunamadı! Koyeb YT_KEYS ayarını kontrol et.")

    # Havuzdan rastgele bir anahtar seçerek günlük kotayı paylaştırır.
    api_key = random.choice(keys)

    # 2. ADIM: YOUTUBE DATA API V3 İLE ARAMA YAP
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
        raise Exception(f"YouTube API Hatası ({response.status_code}): Anahtarlarınızı veya kotanızı kontrol edin.")
    
    data = response.json()
    if not data.get('items'):
        raise Exception("🔍 Aranan parça YouTube üzerinde bulunamadı.")
    
    video_id = data['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    title = data['items'][0]['snippet']['title']
    
    # Kapak fotoğrafı güvenliği
    thumbnails = data['items'][0]['snippet'].get('thumbnails', {})
    thumb = thumbnails.get('high', thumbnails.get('default', {})).get('url', "https://telegra.ph/file/69204068595f57731936c.jpg")

    # 3. ADIM: YT-DLP İLE SES AKIŞ LİNKİNİ AL (GÜÇLENDİRİLMİŞ)
    # "Sign in to confirm you're not a bot" hatasını aşmak için gelişmiş istemci ayarları.
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0', # IPv4 zorlaması
        'geo_bypass': True,
        # YouTube engelini aşmak için güncel tarayıcı kimliği
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        # KRİTİK: YouTube Music ve Mobil istemcileri kullanarak bot kontrolünü atlatır
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'youtube_music', 'mweb'],
                'player_skip': ['webpage', 'configs'],
                'skip': ['dash', 'hls']
            }
        },
        # Gerçek bir kullanıcı gibi ek başlıklar gönderiyoruz
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Upgrade-Insecure-Requests': '1',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False: Sadece ses akış linkini (raw url) alır.
            info = ydl.extract_info(video_url, download=False)
            raw_url
