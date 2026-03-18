import os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream # HATA BURADAYDI: MediaStream yaptık
from yt_dlp import YoutubeDL
from config import Config

assistant = Client("Assistant", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)
call_py = PyTgCalls(assistant)

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
    return f"{02d}:{saniye:02d}"

async def play_music(chat_id, video_info):
    try:
        # Yeni sürümde .play() kullanılır
        await call_py.play(
            chat_id,
            MediaStream(video_info["file_path"])
        )
        return True
    except Exception as e:
        print(f"Oynatma hatası: {e}")
        return False
