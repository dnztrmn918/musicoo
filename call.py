import os
from pyrogram import Client
from pytgcalls import GroupCallFactory # YENİ YAPI: Factory kullanıyoruz
from pytgcalls.types import MediaStream 
from yt_dlp import YoutubeDL
from config import Config

# Asistan (Userbot)
assistant = Client("Assistant", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)

# Ses motoru kurulumu (v2.x Factory yapısı)
call_py = GroupCallFactory(assistant).get_group_call()

ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

queue = []

def get_video_info(query):
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
            return {
                "id": info["id"],
                "title": info["title"],
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "file_path": f"downloads/{info['id']}.mp3"
            }
        except Exception as e:
            print(f"Hata: {e}")
            return None

def saniyeyi_formatla(saniye):
    if saniye is None: return "Bilinmiyor"
    dakika, saniye = divmod(saniye, 60)
    return f"{dakika:02d}:{saniye:02d}"

async def play_music(chat_id, video_info):
    try:
        # Yeni sürüm komutları
        await call_py.join(chat_id)
        await call_py.start_audio(video_info["file_path"])
        return True
    except Exception as e:
        print(f"Oynatma hatası: {e}")
        return False
