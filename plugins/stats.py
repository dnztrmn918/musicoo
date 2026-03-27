import time
import psutil
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db_pool

@Client.on_message(filters.command("durum"))
async def stats_cmd(client, message):
    m = await message.reply_text("📡 **Durum kontrol ediliyor...**")
    start_t = time.time()

    # URL HATASI DÜZELTİLDİ
    try:
        sc_req = requests.get("https://soundcloud.com", timeout=5)
        sc_status = "🟢 Çevrimiçi" if sc_req.status_code == 200 else "🟡 Yavaş"
    except Exception:
        sc_status = "🔴 Erişilemiyor"

    db_ping = "❌ Yok"
    try:
        async with db_pool.acquire() as conn:
            db_s = time.time()
            await conn.execute("SELECT 1")
            db_ping = f"✅ {round((time.time() - db_s)*1000)} ms"
    except:
        pass

    ping = f"{round((time.time() - start_t)*1000)} ms"
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    stats_msg = (
        "╔═══════════════════════╗\n"
        "    📊 𝙎𝙄𝙎𝙏𝙀𝙈 𝘿𝙐𝙍𝙐𝙈𝙐\n"
        "╚═══════════════════════╝\n\n"
        f"⚙️ **Bot Ping:** `{ping}`\n"
        f"🎶 **SoundCloud:** `{sc_status}`\n"
        f"🗄️ **Veritabanı:** {db_ping}\n"
        f"🧠 **CPU:** `%{cpu}` | **RAM:** `%{ram}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕹️ *Sistem aktif ve yayın için hazır.*"
    )

    await m.edit(
        stats_msg,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗑️ Paneli Kapat", callback_data="close_stats")]]
        ),
    )
