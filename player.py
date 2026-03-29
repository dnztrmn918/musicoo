import asyncio
import os
from pytgcalls.types import MediaStream

music_queue = {}
call = None 
userbot = None
bot = None

def get_player_ui():
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Durdur", callback_data="pause"),
         InlineKeyboardButton("▶️ Oynat", callback_data="resume")],
        [InlineKeyboardButton("⏭ Sıradaki", callback_data="skip"),
         InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    return (f"🎶 **Şu anda çalıyor**\n\n📌 **Şarkı:** [{song_info['title']}]({song_info['webpage_url']})\n👤 **İsteyen:** {requested_by}\n\n⚡️ *Keyifli Dinlemeler!*")

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue, call
    
    # --- V2 UYUMLU MOTOR KONTROLÜ ---
    if call is None:
        try:
            from main import call as active_call
            globals()['call'] = active_call
        except: pass

    if chat_id not in music_queue:
        music_queue[chat_id] = []

    if len(music_queue[chat_id]) >= 6:
        return "FULL"

    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        # is_running hatasını burada sildik, sadece call objesini bekliyoruz
        for _ in range(5):
            if call:
                break
            await asyncio.sleep(1)
            
        try:
            # Saf V2 Oynatma
            await call.play(
                chat_id,
                MediaStream(
                    song_info["file_path"], 
                    video_flags=MediaStream.Flags.IGNORE
                )
            )
            return "PLAYING"
        except Exception as e:
            if chat_id in music_queue:
                music_queue[chat_id].pop(0)
            return f"ERROR_DETAIL: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        music_queue[chat_id].pop(0)
        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.play(chat_id, MediaStream(next_song["info"]["file_path"], video_flags=MediaStream.Flags.IGNORE))
                return next_song
            except:
                return await stream_end_handler(chat_id)
        else:
            music_queue.pop(chat_id, None)
            try: await call.leave_call(chat_id)
            except: pass
            return "EMPTY"
    return None
