import time
import psutil
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from database import db_pool

@Client.on_message(filters.command("durum"))
async def stats_cmd(client, message):
    m = await message.reply_text("📡 **Sistem analiz ediliyor...**")
    start_t = time.time()
    
    # 🌩️ SoundCloud Bağlantı Testi
    try:
        sc_req = requests.get("https://soundcloud.com", timeout=5)
        sc_status = "🟢 Çevrimiçi" if sc_req.status_code == 200 else "🟡 Yavaş"
    except:
        sc_status = "🔴 Erişilemiyor"

    # 🗄️ Veritabanı Ping (PostgreSQL)
    db_ping = "Bağlı Değil"
    if db_pool:
        db_s = time.time()
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        db_ping = f"{round((time.time() - db_s) * 1000)} ms"

    ping = f"{round((time.time() - start_t) * 1000)} ms"
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    stats_msg = (
        "🖥️ **MÜZİK SİSTEMİ ANALİZİ**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 **Bot Ping:** `{ping}`\n"
        f"☁️ **SoundCloud:** `{sc_status}`\n"
        f"🗄️ **Veritabanı:** `{db_ping}`\n"
        f"🧠 **CPU Yükü:** `% {cpu}`\n"
        f"💾 **RAM Kullanımı:** `% {ram}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Sorgulayan:** {message.from_user.first_name}\n"
        "✨ *Sistem şu an müzik yayını için optimize.*"
    )

    await m.edit(
        stats_msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑️ Paneli Kapat", callback_data="close_stats")]
        ])
    )
