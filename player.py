import asyncio
from pytgcalls.types import AudioPiped

music_queue = {}
call = None  # main.py tarafından doldurulacak


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


# ────────────────────────────────────────────────
#  KUYRUK VE AKIŞ YÖNETİMİ
# ────────────────────────────────────────────────
async def add_to_queue_or_play(chat_id, song_info, requested_by):
    """Yeni şarkıyı sıraya ekle veya çalmaya başla."""
    global music_queue
    if chat_id not in music_queue:
        music_queue[chat_id] = []

    # Maksimum 5 şarkı sınırı
    if len(music_queue[chat_id]) >= 5:
        return "FULL"

    music_queue[chat_id].append({"info": song_info, "by": requested_by})

    # Eğer ilk şarkıysa direkt çal
    if len(music_queue[chat_id]) == 1:
        try:
            await call.join_group_call(chat_id, AudioPiped(song_info["url"]))
            return "PLAYING"
        except Exception:
            music_queue.pop(chat_id, None)
            return "ERROR"
    return "QUEUED"


async def stream_end_handler(chat_id):
    """Şarkı bittiğinde sıradaki şarkıya geç."""
    if chat_id in music_queue:
        if len(music_queue[chat_id]) > 0:
            music_queue[chat_id].pop(0)

        if len(music_queue[chat_id]) > 0:
            next_song = music_queue[chat_id][0]
            try:
                await call.change_stream(chat_id, AudioPiped(next_song["info"]["url"]))
                return next_song
            except Exception:
                return await stream_end_handler(chat_id)
        else:
            music_queue.pop(chat_id, None)
            try:
                await call.leave_group_call(chat_id)
            except:
                pass
            return "EMPTY"
    return None


# ────────────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ────────────────────────────────────────────────
def format_queue(chat_id):
    """Aktif kuyruk çıktısı."""
    if chat_id not in music_queue or not music_queue[chat_id]:
        return "📭 **Kuyruk boş.**"

    text = "🎼 **Kuyruk Listesi**\n\n"
    for i, s in enumerate(music_queue[chat_id]):
        text += f"**{i + 1}.** {s['info']['title']} — 🎧 {s['by']}\n"
    return text


def clear_queue(chat_id):
    music_queue.pop(chat_id, None)
    return True


def remove_from_queue(chat_id, index: int):
    try:
        removed = music_queue[chat_id].pop(index)
        return removed
    except Exception:
        return None
