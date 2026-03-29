import asyncio
import os
from pytgcalls.types import MediaStream

# Global değişkenler (main.py tarafından doldurulacak)
music_queue = {}
last_message_ids = {}
call = None 
userbot = None
bot = None

def get_player_ui():
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    # Bu butonlar plugins/play.py içindeki callback_query_handler ile konuşur
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Duraklat", callback_data="pause"),
         InlineKeyboardButton("▶️ Devam", callback_data="resume")],
        [InlineKeyboardButton("⏭ Atla", callback_data="skip"),
         InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    # Süre bilgisi varsa al, yoksa 'Bilinmiyor' yaz
    duration = song_info.get('duration', 'Bilinmiyor')
    return (
        f"🎶 **Pi Müzik Oynatılıyor**\n\n"
        f"📌 **Şarkı:** `{song_info['title']}`\n"
        f"⏳ **Süre:** `{duration}`\n"
        f"👤 **İsteyen:** {requested_by}\n\n"
        f"✨ *Keyifli dinlemeler dileriz!*"
    )

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue, call
    if chat_id not in music_queue: music_queue[chat_id] = []
    if len(music_queue[chat_id]) >= 15: return "FULL"

    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            # SES KALİTESİ VE UYUMLULUK İÇİN OPUS CODEC ZORLAMASI
            await call.play(chat_id, MediaStream(
                song_info["file_path"], 
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -vn -acodec libopus -b:a 128k -ar 48000 -ac 2"
            ))
            return "PLAYING"
        except Exception as e:
            if chat_id in music_queue: music_queue[chat_id].pop(0)
            print(f"❌ Oynatma Hatası: {e}")
            return f"ERROR: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    """Şarkı bittiğinde veya atlandığında tetiklenir"""
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
                    ffmpeg_parameters="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -vn -acodec libopus -b:a 128k"
                ))
                
                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=next_song['info']['thumbnail'],
                    caption=f"⏭ **Sıradaki şarkıya geçildi!**\n\n" + format_playing_message(next_song['info'], next_song['by']),
                    reply_markup=get_player_ui()
                )
                last_message_ids[chat_id] = sent_msg.id
                return next_song
            except Exception as e:
                print(f"❌ Geçiş Hatası: {e}")
                return await stream_end_handler(chat_id)
        else:
            # Liste boşaldı
            music_queue.pop(chat_id, None)
            try:
                await call.leave_call(chat_id)
                await bot.send_message(chat_id, "⏹ **Kuyruk bitti, Pi Müzik sesten ayrıldı.**")
            except: pass
            return "EMPTY"
    return None

# --- YÖNETİM FONKSİYONLARI ---

def clear_entire_queue(chat_id):
    if chat_id in music_queue:
        music_queue.pop(chat_id, None)

def clear_queue_except_current(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        current = music_queue[chat_id][0]
        music_queue[chat_id] = [current]

def remove_song_from_queue(chat_id, index):
    if chat_id in music_queue and 0 <= index < len(music_queue[chat_id]):
        return music_queue[chat_id].pop(index)
    return None

async def pause_stream(chat_id):
    try:
        await call.pause_stream(chat_id)
        return True
    except: return False

async def resume_stream(chat_id):
    try:
        await call.resume_stream(chat_id)
        return True
    except: return False
