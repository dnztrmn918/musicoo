from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

music_queue = {}
call = None

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
    return (
        f"🎵 **Şu An Oynatılıyor**\n\n"
        f"📌 **İsim:** [{song_info['title']}]({song_info['webpage_url']})\n"
        f"⏱ **Süre:** `{song_info['duration']}`\n"
        f"👤 **Talep Eden:** {requested_by}"
    )

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue
    
    if chat_id not in music_queue:
        music_queue[chat_id] = []
        
    music_queue[chat_id].append({"info": song_info, "by": requested_by})
    
    if len(music_queue[chat_id]) == 1:
        await call.join_group_call(
            chat_id,
            AudioPiped(song_info['url'])
        )
        return True
    return False
