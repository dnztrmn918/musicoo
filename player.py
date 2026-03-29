import asyncio
import os
from pytgcalls.types import MediaStream

# Global değişkenler (main.py tarafından doldurulacak)
music_queue = {}
last_message_ids = {}
call = None 
userbot = None
bot = None

# --- YENİ EKLENEN AKILLI SİLME FONKSİYONU ---
def safe_delete(file_path):
    """Dosyanın başka bir grupta çalınmadığından emin olup sunucudan siler"""
    if not file_path or not os.path.exists(file_path):
        return
    
    # Şarkı hala başka bir grubun kuyruğunda var mı diye kontrol ediyoruz
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
            print(f"🗑️ Temizlik: {file_path} sunucudan silindi.")
        except Exception as e:
            print(f"⚠️ Dosya silinemedi: {e}")
# ---------------------------------------------

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
            # FİZİKSEL DOSYA ÇALINDIĞI İÇİN FFMPEG PARAMETRELERİ SADELEŞTİRİLDİ
            await call.play(chat_id, MediaStream(
                song_info["file_path"], 
                video_flags=MediaStream.Flags.IGNORE
            ))
            return "PLAYING"
        except Exception as e:
            if chat_id in music_queue: 
                failed_song = music_queue[chat_id].pop(0)
                safe_delete(failed_song["info"]["file_path"]) # Hata verirse direkt sil
            print(f"❌ Oynatma Hatası: {e}")
            return f"ERROR: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    """Şarkı bittiğinde veya atlandığında tetiklenir"""
    global last_message_ids, music_queue
    if chat_id in music_queue and len(music_queue[chat_id]) > 0:
        
        # Biten şarkıyı kuyruktan çıkar ve sunucudan SİL
        finished_song = music_queue[chat_id].pop(0)
        safe_delete(finished_song["info"]["file_path"])
        
        # Eski mesajı temizle
        if chat_id in last_message_ids:
            try: await bot.delete_messages(chat_id, last_message_ids[chat_id])
            except: pass

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                # SIRADAKİ FİZİKSEL DOSYAYI ÇAL
                await call.play(chat_id, MediaStream(
                    next_song["info"]["file_path"], 
                    video_flags=MediaStream.Flags.IGNORE
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
        queue = music_queue.pop(chat_id, None)
        if queue:
            for song in queue:
                safe_delete(song["info"]["file_path"])

def clear_queue_except_current(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        current = music_queue[chat_id][0]
        removed_songs = music_queue[chat_id][1:]
        music_queue[chat_id] = [current]
        for song in removed_songs:
            safe_delete(song["info"]["file_path"])

def remove_song_from_queue(chat_id, index):
    if chat_id in music_queue and 0 <= index
