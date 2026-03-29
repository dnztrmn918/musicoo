import asyncio
import os
from pytgcalls.types import MediaStream

# Global değişkenler
music_queue = {}
last_message_ids = {}
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
    return (f"🎶 **Şu anda çalıyor**\n\n📌 **Şarkı:** [{song_info['title']}]({song_info['webpage_url']})\n"
            f"👤 **İsteyen:** {requested_by}\n\n⚡️ *Zirve2 Keyifli Dinlemeler Diler!*")

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue, call
    if chat_id not in music_queue: music_queue[chat_id] = []
    if len(music_queue[chat_id]) >= 10: return "FULL"

    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            # SES GELMEME SORUNUNU ÇÖZEN FFMPEG PARAMETRELERİ
            await call.play(chat_id, MediaStream(
                song_info["file_path"], 
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            ))
            return "PLAYING"
        except Exception as e:
            if chat_id in music_queue: music_queue[chat_id].pop(0)
            print(f"❌ Play Hatası: {e}")
            return f"ERROR: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    global last_message_ids, music_queue
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        music_queue[chat_id].pop(0)
        
        # Eski mesajı temizle
        if chat_id in last_message_ids:
            try: await bot.delete_messages(chat_id, last_message_ids[chat_id])
            except: pass

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.play(chat_id, MediaStream(
                    next_song["info"]["file_path"], 
                    video_flags=MediaStream.Flags.IGNORE,
                    ffmpeg_parameters="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                ))
                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=next_song['info']['thumbnail'],
                    caption=f"⏭ **Sıradaki şarkıya geçildi!**\n\n" + format_playing_message(next_song['info'], next_song['by']),
                    reply_markup=get_player_ui()
                )
                last_message_ids[chat_id] = sent_msg.id
                return next_song
            except:
                return await stream_end_handler(chat_id)
        else:
            music_queue.pop(chat_id, None)
            try:
                await call.leave_call(chat_id)
                await bot.send_message(chat_id, "⏹ **Kuyruk bitti, asistan sesten ayrıldı.**")
            except: pass
            return "EMPTY"
    return None

# --- LOGLARDAKİ AttributeError HATALARINI ÇÖZEN FONKSİYONLAR ---
def clear_entire_queue(chat_id):
    """Tüm kuyruğu temizler (stop komutu için)"""
    if chat_id in music_queue:
        music_queue.pop(chat_id, None)

def clear_queue_except_current(chat_id):
    """Şu an çalan hariç kuyruğu temizler"""
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        current = music_queue[chat_id][0]
        music_queue[chat_id] = [current]

def remove_song_from_queue(chat_id, index):
    """Belirli bir şarkıyı kuyruktan siler (del komutu için)"""
    if chat_id in music_queue and 0 <= index < len(music_queue[chat_id]):
        return music_queue[chat_id].pop(index)
    return None
