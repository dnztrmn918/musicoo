import os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL
from config import Config

# Asistan Hesabı (Userbot)
assistant = Client("Assistant", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)
call_py = PyTgCalls(assistant)

# YouTube Ayarları
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

# Müzik Kuyruğu
queue = []

def get_video_info(query):
    """YouTube'dan şarkı bilgilerini ve indirme linkini alır."""
    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Arama yap
            info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
            
            # Gerekli bilgileri topla
            video_info = {
                "id": info["id"],
                "title": info["title"],
                "duration": info.get("duration"), # Saniye cinsinden süre
                "thumbnail": info.get("thumbnail"), # Kapak fotoğrafı linki
                "file_path": f"downloads/{info['id']}.mp3"
            }
            return video_info
        except Exception as e:
            print(f"YouTube hatası: {e}")
            return None

def saniyeyi_formatla(saniye):
    """Saniyeyi DD:SS formatına çevirir."""
    if saniye is None:
        return "Bilinmiyor"
    dakika, saniye = divmod(saniye, 60)
    return f"{dakika:02d}:{saniye:02d}"

async def play_music(chat_id, video_info):
    """Asistanı sesli sohbete sokar ve müziği çalar."""
    try:
        await call_py.join_group_call(
            chat_id,
            AudioPiped(video_info["file_path"])
        )
        return True
    except Exception as e:
        print(f"Sohbete katılma hatası: {e}")
        return False
