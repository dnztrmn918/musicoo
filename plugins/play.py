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
    # Dosya silme ve RAM temizleme (Çöp Toplayıcı) işlemi
    if not file_path or not os.path.exists(file_path): return
    # Dosyanın kuyruktaki başka bir şarkı tarafından KULLANILMADIĞINDAN emin ol
    is_used = any(song["info"].get("file_path") == file_path for queue in music_queue.values() for song in queue)
    if not is_used:
        try:
            os.remove(file_path)
            gc.collect() # RAM'i rahatlat
        except: pass

def get_player_ui():
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ Durdur", callback_data="pause"), InlineKeyboardButton("▶️ Devam", callback_data="resume")],
        [InlineKeyboardButton("⏭ Geç", callback_data="skip"), InlineKeyboardButton("⏹ Bitir", callback_data="end")]
    ])

def format_playing_message(song_info, requested_by):
    duration = song_info.get('duration', 'Bilinmiyor')
    return (
        f"🎶 **Şu An Çalıyor**\n\n"
        f"📌 **Parça:** `{song_info['title']}`\n"
        f"⏳ **Süre:** `{duration}`\n"
        f"👤 **Talep Eden:** {requested_by}"
    )

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue, call
    if chat_id not in music_queue: music_queue[chat_id] = []
    
    queue_pos = len(music_queue[chat_id])
    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            # PyTgCalls v2 formatıyla direkt oynat
            await call.play(chat_id, MediaStream(song_info["file_path"]))
            return "PLAYING", None
        except Exception as e:
            if chat_id in music_queue: music_queue[chat_id].pop(0)
            safe_delete(song_info["file_path"]) # Hata verirse çöp dosya kalmasın, sil
            return "ERROR", f"{str(e)}"
    
    return "QUEUED", queue_pos

async def stream_end_handler(chat_id, action="auto"):
    global last_message_ids, music_queue

    # 1. EĞER "BİTİR (END)" KOMUTU GELDİYSE
    if action == "end":
        clear_entire_queue(chat_id)
        try: await call.leave_call(chat_id)
        except: pass
        if chat_id in last_message_ids:
            try: 
                await bot.delete_messages(chat_id, last_message_ids[chat_id])
                del last_message_ids[chat_id]
            except: pass
        await bot.send_message(chat_id, "🛑 **Yayın sonlandırıldı. Kuyruk temizlendi ve asistan sesli sohbetten ayrıldı.**")
        return

    # 2. ŞARKI KENDİLİĞİNDEN BİTTİYSE VEYA "ATLA (SKIP)" YAPILDIYSA
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        # Biten/Atlanan şarkıyı listeden çıkar ve DOSYASINI SİL
        finished_song = music_queue[chat_id].pop(0)
        safe_delete(finished_song["info"].get("file_path"))
        
        # Eski mesajı sil
        if chat_id in last_message_ids:
            try: 
                await bot.delete_messages(chat_id, last_message_ids[chat_id])
                del last_message_ids[chat_id]
            except: pass

        # Sırada başka şarkı varsa onu çal
        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.play(chat_id, MediaStream(next_song["info"]["file_path"]))
                
                if action == "skip":
                    caption = (
                        f"⏭ **Parça Atlandı!**\n"
                        f"❌ **Atlanan:** `{finished_song['info']['title']}`\n\n"
                        f"🎧 **Şu An Oynatılan:**\n"
                        f"📌 `{next_song['info']['title']}`\n"
                        f"⏳ **Süre:** `{next_song['info'].get('duration', 'Bilinmiyor')}`\n"
                        f"👤 **Talep Eden:** {next_song['by']}"
                    )
                else:
                    caption = f"⏭ **Sıradaki Parçaya Geçildi!**\n\n" + format_playing_message(next_song['info'], next_song['by'])

                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=next_song['info'].get('thumbnail') or "plugins/logo.jpg",
                    caption=caption,
                    reply_markup=get_player_ui()
                )
                last_message_ids[chat_id] = sent_msg.id
            except Exception as e:
                print(f"Sıradakine geçiş hatası: {e}")
                return await stream_end_handler(chat_id, action)
        
        # Sırada şarkı kalmadıysa
        else:
            music_queue.pop(chat_id, None)
            try: await call.leave_call(chat_id)
            except: pass
            
            if action == "skip":
                await bot.send_message(chat_id, "🛑 **Kuyrukta şarkı yok, asistan sesli sohbetten ayrılıyor.**")
            else:
                await bot.send_message(chat_id, "🛑 **Kuyruk bitti, asistan sesten ayrıldı.**")
    else:
        try: await call.leave_call(chat_id)
        except: pass

def clear_entire_queue(chat_id):
    if chat_id in music_queue:
        queue = music_queue.pop(chat_id, None)
        if queue:
            for song in queue:
                safe_delete(song["info"].get("file_path")) # Kuyruktaki tüm indirilenleri sil

def clear_queue_except_current(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        current = music_queue[chat_id][0]
        removed_songs = music_queue[chat_id][1:]
        music_queue[chat_id] = [current]
        for song in removed_songs:
            safe_delete(song["info"].get("file_path")) # Sadece silinenlerin dosyalarını temizle

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
