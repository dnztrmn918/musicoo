import asyncio
import os
from pytgcalls.types import MediaStream, AudioQuality
from pytgcalls import filters as fl
import gc

# Global değişkenler (main.py tarafından doldurulacak)
music_queue = {}
last_message_ids = {}
call = None 
userbot = None
bot = None

# 🔥 v2.x İÇİN EN STABİL PARAMETRELER: Headers eklendi (Ses gelmeme sorununu çözer)
FFMPEG_PARAMS = (
    '-headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" '
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
)

# --- AKILLI SİLME FONKSİYONU ---
def safe_delete(file_path):
    """Fiziksel indirme kalıntılarını temizler"""
    if not file_path or not os.path.exists(file_path):
        return
    
    is_used = False
    for queue in music_queue.values():
        for song in queue:
            if song["info"].get("file_path") == file_path:
                is_used = True
                break
        if is_used: break
        
    if not is_used:
        try:
            os.remove(file_path)
            gc.collect() 
            print(f"🗑️ Temizlik: {file_path} sunucudan silindi.")
        except Exception as e:
            print(f"⚠️ Dosya silinemedi: {e}")

def get_player_ui():
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Duraklat", callback_data="pause"),
         InlineKeyboardButton("▶️ Devam", callback_data="resume")],
        [InlineKeyboardButton("⏭ Atla", callback_data="skip"),
         InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
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
            # 🔥 ONLINE LİNK İÇİN DOĞRU YAPILANDIRMA
            await call.play(chat_id, MediaStream(
                song_info["file_path"], 
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=FFMPEG_PARAMS,
                audio_parameters=AudioQuality.HIGH
            ))
            return "PLAYING"
        except Exception as e:
            if chat_id in music_queue: 
                music_queue[chat_id].pop(0)
            print(f"❌ Oynatma Hatası: {e}")
            return f"ERROR: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    """Şarkı bittiğinde veya atlandığında tetiklenir"""
    global last_message_ids, music_queue
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        
        finished_song = music_queue[chat_id].pop(0)
        safe_delete(finished_song["info"]["file_path"])
        
        if chat_id in last_message_ids:
            try: await bot.delete_messages(chat_id, last_message_ids[chat_id])
            except: pass

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.play(chat_id, MediaStream(
                    next_song["info"]["file_path"], 
                    video_flags=MediaStream.Flags.IGNORE,
                    ffmpeg_parameters=FFMPEG_PARAMS,
                    audio_parameters=AudioQuality.HIGH
                ))
                
                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=next_song['info']['thumbnail'],
                    caption=f"⏭ **Sıradaki şarkıya geçildi!**\n\n" + format_playing_message(next_song['info'], next_song['by']),
                    reply_markup=get_player_ui()
                )
                last_message_ids[chat_id] = sent_msg.id
            except Exception as e:
                print(f"❌ Geçiş Hatası: {e}")
                return await stream_end_handler(chat_id)
        else:
            music_queue.pop(chat_id, None)
            try:
                await call.leave_call(chat_id)
                await bot.send_message(chat_id, "⏹ **Kuyruk bitti, Pi Müzik sesten ayrıldı.**")
            except: pass
    return None

async def stream_ended_handler_wrapper(_, update):
    return await stream_end_handler(update.chat_id)

# --- YÖNETİM FONKSİYONLARI (Kilitlenmeyi Önleyen Yapı) ---

def clear_entire_queue(chat_id):
    if chat_id in music_queue:
        queue = music_queue.pop(chat_id, None)
        if queue:
            for song in queue:
                safe_delete(song["info"]["file_path"])

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
