from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped

music_queue = {}
call = None  

def get_player_ui():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Durdur", callback_data="pause"), InlineKeyboardButton("▶️ Oynat", callback_data="resume")],
        [InlineKeyboardButton("⏭ Sıradaki", callback_data="skip"), InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    return (
        f"🎵 **Şu An Oynatılıyor**\n\n"
        f"📌 **İsim:** [{song_info['title']}]({song_info['webpage_url']})\n"
        f"👤 **Talep Eden:** {requested_by}"
    )

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue
    if chat_id not in music_queue:
        music_queue[chat_id] = []
    if len(music_queue[chat_id]) >= 5:
        return "FULL"
    music_queue[chat_id].append({"info": song_info, "by": requested_by})
    if len(music_queue[chat_id]) == 1:
        await call.join_group_call(chat_id, AudioPiped(song_info['url']))
        return "PLAYING"
    return "QUEUED"

async def stream_end_handler(chat_id):
    if chat_id in music_queue:
        if len(music_queue[chat_id]) > 1:
            music_queue[chat_id].pop(0) 
            next_song = music_queue[chat_id][0]
            await call.change_stream(chat_id, AudioPiped(next_song['info']['url']))
            return next_song
        else:
            music_queue.pop(chat_id, None)
            await call.leave_group_call(chat_id)
            return "EMPTY"
    return None
