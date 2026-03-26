import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# Şarkı sırası ve çağrı yönetimi
music_queue = {}
call = None  # Bu, main.py içindeki PyTgCalls objesi ile bağlanmalı

# YouTube Bot Engelini ve SABR Hatasını Aşan Gelişmiş Ayarlar
YDL_OPTS = {
    "format": "bestaudio/best",
    "cookiefile": "cookies.txt",  # Yüklediğin çerez dosyasını kullanır
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "source_address": "0.0.0.0",
    # YouTube'un yeni kısıtlamalarını (SABR) aşmak için istemci taklidi:
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "ios"],
            "skip": ["webpage", "hls"]
        }
    }
}

def get_player_ui():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Durdur", callback_data="pause"),
            InlineKeyboardButton("▶️ Oynat", callback_data="resume")
        ],
        [
            InlineKeyboardButton("⏭ Sıradaki", callback_data="skip"),
            InlineKeyboardButton("⏹ Bitir", callback_data="end")
        ]
    ])

def format_playing_message(song_info, requested_by):
    # Süre formatı (Saniye cinsinden gelirse dakikaya çevirir)
    duration = song_info.get('duration')
    if isinstance(duration, int):
        mins, secs = divmod(duration, 60)
        duration = f"{mins:02d}:{secs:02d}"
    else:
        duration = "Bilinmiyor"

    return (
        f"🎵 **Şu An Oynatılıyor**\n\n"
        f"📌 **İsim:** [{song_info['title']}]({song_info['webpage_url']})\n"
        f"⏱ **Süre:** `{duration}`\n"
        f"👤 **Talep Eden:** {requested_by}\n\n"
        f"🎧 **Pi-Müzik Keyifli Dinlemeler Diler!**"
    )

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue
    
    if chat_id not in music_queue:
        music_queue[chat_id] = []
        
    music_queue[chat_id].append({"info": song_info, "by": requested_by})
    
    if len(music_queue[chat_id])
