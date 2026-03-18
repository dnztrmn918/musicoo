import os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream 
from yt_dlp import YoutubeDL
from config import Config

# Asistan (Userbot) kurulumu
assistant = Client(
    "Assistant", 
    api_id=Config.API_ID, 
    api_hash=Config.API_HASH, 
    session_string=Config.STRING_SESSION
)

# Ses motoru kurulumu
call_py = PyTgCalls(assistant)

# YouTube ayarları (En güncel yt-dlp standartları)
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
            print(f"Arama Hatası: {e}")
            return None

async def play_music(chat_id, video_info):
    try:
        # GÜNCEL KOMUT: play_music yerine sadece play kullanılır
        await call_py.play(
            chat_id,
            MediaStream(video_info["file_path"])
        )
        return True
    except Exception as e:
        print(f"Oynatma Hatası: {e}")
        return False
