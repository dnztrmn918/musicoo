import asyncio
import os
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
import gc

music_queue = {}
last_message_ids = {}
call = None 
userbot = None
bot = None

# 🔥 SESİ %100 GARANTİ EDEN AYAR (Formatı ve gecikmeyi zorla çözer)
FFMPEG_PARAMS = (
    '-headers "User-Agent: Mozilla/5.0" '
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
    '-probesize 32 -analyzeduration 0 '
    '-af "volume=1.2" -c:a pcm_s16le -ac 2 -ar 48000' 
)

def safe_delete(file_path):
    if not file_path or not os.path.exists(file_path): return
    is_used = any(song["info"].get("file_path") == file_path for queue in music_queue.values() for song in queue)
    if not is_used:
        try:
            os.remove(file_path)
            gc.collect() 
        except: pass

def get_player_ui():
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Dur", callback_data="pause"), InlineKeyboardButton("▶️ Devam", callback_data="resume")],
        [InlineKeyboardButton("⏭ Atla", callback_data="skip"), InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    duration = song_info.get('duration', 'Bilinmiyor')
    return f"🎶 **Pi Müzik Oynatılıyor**\n\n📌 **Şarkı:** `{song_info['title']}`\n⏳ **Süre:** `{duration}`\n👤 **İsteyen:** {requested_by}"

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue, call
    if chat_id not in music_queue: music_queue[chat_id] = []
    
    # Yeni şarkı eklenirken bilgiyi formatlı döndürüyoruz
    queue_pos = len(music_queue[chat_id])
    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            # 🔥 V2 İÇİN DOĞRU SES AKIŞI (AudioPiped)
            await call.play(chat_id, AudioPiped(
                song_info["file_path"], 
                HighQualityAudio(),
                ffmpeg_parameters=FFMPEG_PARAMS
            ))
            return "PLAYING", None
        except Exception as e:
            if chat_id in music_queue: music_queue[chat_id].pop(0)
            return "ERROR", f"{str(e)}"
    
    # Çalan varsa kuyruk bilgisi döner
    return "QUEUED", queue_pos

async def stream_end_handler(chat_id):
    global last_message_ids, music_queue
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        
        finished_song = music_queue[chat_id].pop(0)
        safe_delete(finished_song["info"].get("file_path"))
        
        # Eski Mesajı Silme İyileştirmesi
        if chat_id in last_message_ids:
            try: 
                await bot.delete_messages(chat_id, last_message_ids[chat_id])
                del last_message_ids[chat_id]
            except: pass

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                # 🔥 V2'DE SIRADAKİNE GEÇİŞ (change_stream)
                await call.change_stream(chat_id, AudioPiped(
                    next_song["info"]["file_path"], 
                    HighQualityAudio(),
                    ffmpeg_parameters=FFMPEG_PARAMS
                ))
                
                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=next_song['info']['thumbnail'],
                    caption=f"⏭ **Sıradaki Parçaya Geçildi!**\n\n" + format_playing_message(next_song['info'], next_song['by']),
                    reply_markup=get_player_ui()
                )
                last_message_ids[chat_id] = sent_msg.id
            except Exception as e:
                print(f"Sıradakine geçiş hatası: {e}")
                return await stream_end_handler(chat_id)
        else:
            # 🔥 İSTEDİĞİN ÇIKIŞ MESAJI VE İŞLEVİ
            music_queue.pop(chat_id, None)
            try:
                await call.leave_call(chat_id)
                await bot.send_message(chat_id, "🛑 **Kuyrukta parça kalmadı, yayın sonlandırıldı. Tekrar müzik dinlemek için `/play` komutunu kullanın.**")
            except: pass
    return None

def clear_entire_queue(chat_id):
    if chat_id in music_queue: music_queue.pop(chat_id, None)

def clear_queue_except_current(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        music_queue[chat_id] = [music_queue[chat_id][0]]

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
