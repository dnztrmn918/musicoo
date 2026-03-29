import asyncio
import os
import gc
from pytgcalls.types import MediaStream

music_queue = {}
last_message_ids = {}
call = None 
userbot = None
bot = None

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
    
    queue_pos = len(music_queue[chat_id])
    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            # 🔥 FİZİKSEL DOSYA DOĞRUDAN OYNATILIR (Kesintisiz Ses)
            await call.play(chat_id, MediaStream(
                song_info["file_path"], 
                video_flags=MediaStream.Flags.IGNORE
            ))
            return "PLAYING", None
        except Exception as e:
            if chat_id in music_queue: music_queue[chat_id].pop(0)
            return "ERROR", f"{str(e)}"
    
    return "QUEUED", queue_pos

async def stream_end_handler(chat_id, action="skip"):
    global last_message_ids, music_queue
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        
        finished_song = music_queue[chat_id].pop(0)
        safe_delete(finished_song["info"].get("file_path"))
        
        if chat_id in last_message_ids:
            try: 
                await bot.delete_messages(chat_id, last_message_ids[chat_id])
                del last_message_ids[chat_id]
            except: pass

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.play(chat_id, MediaStream(
                    next_song["info"]["file_path"], 
                    video_flags=MediaStream.Flags.IGNORE
                ))
                
                # 🔥 İSTEDİĞİN DETAYLI ATLANDI MESAJI
                if action == "skip":
                    caption = (
                        f"⏭ **Parça Atlandı!**\n"
                        f"❌ **Atlanan:** `{finished_song['info']['title']}`\n\n"
                        f"🎧 **Şu An Çalan:**\n"
                        f"📌 `{next_song['info']['title']}`\n"
                        f"👤 **İsteyen:** {next_song['by']}"
                    )
                else:
                    caption = f"⏭ **Sıradaki Parçaya Geçildi!**\n\n" + format_playing_message(next_song['info'], next_song['by'])

                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=next_song['info']['thumbnail'],
                    caption=caption,
                    reply_markup=get_player_ui()
                )
                last_message_ids[chat_id] = sent_msg.id
            except Exception as e:
                print(f"Sıradakine geçiş hatası: {e}")
                return await stream_end_handler(chat_id, action)
        else:
            music_queue.pop(chat_id, None)
            try: await call.leave_call(chat_id)
            except: pass
            
            # 🔥 İSTEDİĞİN BİTİRİLDİ MESAJI
            if action == "end":
                await bot.send_message(chat_id, "🛑 **Yayın sonlandırıldı. Kuyrukta parça kalmadığı için asistan sesli sohbetten ayrıldı.\nTekrar şarkı oynatmak için `/play` komutunu kullanın.**")
            else:
                await bot.send_message(chat_id, "🛑 **Kuyruk bitti, asistan sesten ayrıldı.**")
    else:
        try: await call.leave_call(chat_id)
        except: pass

    return None

def clear_entire_queue(chat_id):
    if chat_id in music_queue:
        queue = music_queue.pop(chat_id, None)
        if queue:
            for song in queue:
                safe_delete(song["info"].get("file_path"))

def clear_queue_except_current(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        current = music_queue[chat_id][0]
        removed_songs = music_queue[chat_id][1:]
        music_queue[chat_id] = [current]
        for song in removed_songs:
            safe_delete(song["info"].get("file_path"))

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
