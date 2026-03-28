import asyncio
import os
# v0.9.7 için doğru içe aktarmalar eklendi
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped

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
    return (
        f"🎶 **Şu anda çalıyor**\n\n"
        f"📌 **Şarkı:** [{song_info['title']}]({song_info['webpage_url']})\n"
        f"👤 **İsteyen:** {requested_by}\n\n"
        f"⚡️ *Keyifli Dinlemeler!*"
    )

def safe_delete(file_path):
    if not file_path or str(file_path).startswith("http"):
        return
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

async def add_to_queue_or_play(chat_id, song_info, requested_by):
    global music_queue
    if chat_id not in music_queue:
        music_queue[chat_id] = []

    # 1 Çalan + 5 Kuyruk = Toplam 6 sınır
    if len(music_queue[chat_id]) >= 6:
        safe_delete(song_info.get("file_path"))
        return "FULL"

    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    if len(music_queue[chat_id]) == 1:
        try:
            if userbot:
                try: await userbot.get_chat(chat_id)
                except: pass
            
            # KRİTİK DÜZELTME: v0.9.7 motoru için stream_type eklendi
            await call.join_group_call(
                chat_id, 
                AudioPiped(song_info["file_path"]),
                stream_type=StreamType().pulse_stream
            )
            return "PLAYING"
        except Exception as e:
            if music_queue[chat_id]:
                failed_song = music_queue[chat_id].pop(0)
                safe_delete(failed_song["info"].get("file_path"))
            return f"ERROR_DETAIL: {str(e)}"
    return "QUEUED"

async def stream_end_handler(chat_id):
    if chat_id in music_queue:
        if len(music_queue[chat_id]) > 0:
            finished_song = music_queue[chat_id].pop(0)
            safe_delete(finished_song["info"].get("file_path"))

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                # KRİTİK DÜZELTME: v0.9.7 uyumlu şarkı atlama komutu
                await call.change_stream(
                    chat_id, 
                    AudioPiped(next_song["info"]["file_path"])
                )
                return next_song
            except Exception:
                return await stream_end_handler(chat_id)
        else:
            music_queue.pop(chat_id, None)
            try: await call.leave_group_call(chat_id)
            except: pass
            return "EMPTY"
    return None

def clear_entire_queue(chat_id):
    if chat_id in music_queue:
        for song in music_queue[chat_id]:
            safe_delete(song["info"].get("file_path"))
        music_queue.pop(chat_id, None)

def clear_queue_except_current(chat_id):
    if chat_id in music_queue and len(music_queue[chat_id]) > 1:
        current = music_queue[chat_id][0]
        for song in music_queue[chat_id][1:]:
            safe_delete(song["info"].get("file_path"))
        music_queue[chat_id] = [current]

def remove_song_from_queue(chat_id, index):
    if chat_id in music_queue and 0 <= index < len(music_queue[chat_id]):
        removed = music_queue[chat_id].pop(index)
        safe_delete(removed["info"].get("file_path"))
        return removed
    return None
