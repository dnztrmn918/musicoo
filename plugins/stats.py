import time
import psutil
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import player
from main import START_TIME # Botun açılış zamanı

def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d > 0: return f"{d} gün, {h} saat, {m} dakika"
    elif h > 0: return f"{h} saat, {m} dakika"
    elif m > 0: return f"{m} dakika, {s} saniye"
    return f"{s} saniye"

# --- /DURUM KOMUTU (Müzik Sistemi) ---
@Client.on_message(filters.command(["durum", "stats"]))
async def status_cmd(client, message: Message):
    msg = await message.reply("📊 Durum kontrol ediliyor...")
    try:
        r = requests.get("https://www.youtube.com", timeout=3)
        yt_status = "✅ Aktif (Bağlı)" if r.status_code == 200 else f"⚠️ Yavaş (HTTP {r.status_code})"
    except:
        yt_status = "❌ Bağlantı Hatası"
        
    queue_count = sum(len(q) for q in player.music_queue.values())
    active_chats = len(player.music_queue)
        
    text = (
        "📊 **Sistem Durumu:**\n\n"
        "🤖 **Bot:** Çevrimiçi\n"
        "👤 **Asistan:** Aktif\n"
        f"🎥 **YouTube:** {yt_status}\n\n"
        f"🎧 **Aktif Sesli Sohbet:** {active_chats}\n"
        f"🎶 **Kuyruktaki Toplam Şarkı:** {queue_count}"
    )
    await msg.edit(text)

# --- /BİLGİ KOMUTU (Sunucu Sistemi) ---
@Client.on_message(filters.command(["bilgi", "info"]))
async def info_cmd(client, message: Message):
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = get_readable_time(uptime_sec)
    
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ram_usage = f"{ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB ({ram.percent}%)"
    
    text = (
        "ℹ️ **Sistem ve Sunucu Bilgileri:**\n\n"
        f"⏱ **Çalışma Süresi (Uptime):** {uptime_str}\n"
        f"💻 **CPU Kullanımı:** %{cpu_usage}\n"
        f"💾 **RAM Kullanımı:** {ram_usage}\n"
        f"🌐 **Altyapı:** Pyrogram & PyTgCalls"
    )
    await message.reply(text)
