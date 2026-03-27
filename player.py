import asyncio
from pytgcalls.types import AudioPiped

music_queue = {}
call = None    # main.py tarafından doldurulacak
userbot = None # main.py tarafından doldurulacak
bot = None     # main.py tarafından doldurulacak

def get_player_ui():
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Durdur", callback_data="pause"),
         InlineKeyboardButton("▶️ Oynat", callback_data="resume")],
        [InlineKeyboardButton("⏭ Sıradaki", callback_data="skip"),
         InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    return (
        f"🎶 **Şu anda çalıyor**\n\n"
        f"📌 **Şarkı:** [{song_info['title']}]({song_info['webpage_url']})\n"
        f"👤 **İsteyen:** {requested_by}\n\n"
        f"⚡️ *Keyifli Dinlemeler!*"
    )

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue
    if chat_id not in music_queue:
        music_queue[chat_id] = []

    if len(music_queue[chat_id]) >= 5:
        return "FULL"

    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            # Userbot'un grubu hafızasına alması için ufak bir ping atıyoruz
            if userbot:
                await userbot.get_chat(chat_id) 
            await call.join_group_call(chat_id, AudioPiped(song_info["url"]))
            return "PLAYING"
        except Exception as e:
            music_queue.pop(chat_id, None)
            return f"ERROR_DETAIL: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    if chat_id in music_queue:
        if len(music_queue[chat_id]) > 0:
            music_queue[chat_id].pop(0)

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.change_stream(chat_id, AudioPiped(next_song["info"]["url"]))
                return next_song
            except Exception:
                return await stream_end_handler(chat_id)
        else:
            music_queue.pop(chat_id, None)
            try:
                await call.leave_group_call(chat_id)
            except:
                pass
            return "EMPTY"
    return None
