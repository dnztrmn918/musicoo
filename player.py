from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped
import asyncio

music_queue = {}
call = None  

def get_player_ui():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Durdur", callback_data="pause"), InlineKeyboardButton("▶️ Oynat", callback_data="resume")],
        [InlineKeyboardButton("⏭ Sıradaki", callback_data="skip"), InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    return (
        f"🎶 **Şu An Oynatılıyor**\n\n"
        f"📌 **İsim:** [{song_info['title']}]({song_info['webpage_url']})\n"
        f"👤 **Talep Eden:** {requested_by}\n\n"
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
            await call.join_group_call(chat_id, AudioPiped(song_info['url']))
            return "PLAYING"
        except Exception:
            music_queue.pop(chat_id, None) # Hata anında kuyruğu sil ki kilitlenmesin 
            return "ERROR"
    return "QUEUED"

async def stream_end_handler(chat_id):
    if chat_id in music_queue:
        # Mevcut şarkıyı listeden kesin olarak çıkar 
        if len(music_queue[chat_id]) > 0:
            music_queue[chat_id].pop(0) 
        
        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.change_stream(chat_id, AudioPiped(next_song['info']['url']))
                return next_song
            except Exception:
                return await stream_end_handler(chat_id)
        else:
            # Kuyruk bittiğinde veriyi temizle 
            music_queue.pop(chat_id, None)
            try: await call.leave_group_call(chat_id)
            except: pass
            return "EMPTY"
    return None
