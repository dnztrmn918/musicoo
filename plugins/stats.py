import time
import psutil
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db_pool, get_served_users, get_served_chats, is_sudo
import main
import config

# ────────────────────────────────────────────────
# HERKESE AÇIK DURUM KOMUTU (/durum)
# ────────────────────────────────────────────────
@Client.on_message(filters.command("durum"))
async def stats_cmd(client, message):
    m = await message.reply_text("📡 **Durum kontrol ediliyor...**")
    start_t = time.time()

    # Aktiflik süresi (Uptime) hesaplama
    uptime_sec = int(time.time() - main.START_TIME)
    mins, secs = divmod(uptime_sec, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    uptime_str = f"{days}g {hours}s {mins}d {secs}s" if days > 0 else f"{hours}s {mins}d {secs}s"

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
        f"⏱ **Aktiflik:** `{uptime_str}`\n"
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


# ────────────────────────────────────────────────
# SADECE YÖNETİCİLERE (SUDO) ÖZEL BİLGİ KOMUTU (/bilgi)
# ────────────────────────────────────────────────
@Client.on_message(filters.command("bilgi"))
async def bot_info(client, message):
    if not await is_sudo(message.from_user.id):
        return await message.reply("⛔ **Yalnızca SUDO kullanıcıları erişebilir.**")

    uptime_sec = int(time.time() - main.START_TIME)
    m, s = divmod(uptime_sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    uptime = f"{d} gün, {h} saat, {m} dk" if d > 0 else f"{h} saat, {m} dakika, {s} saniye"
    start_date = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(main.START_TIME))

    ping_start = time.time()
    try:
        sc = requests.get("https://soundcloud.com", timeout=5)
        sc_stat = "🟢 Aktif" if sc.status_code == 200 else "🟡 Yavaş"
    except:
        sc_stat = "🔴 Kapalı"

    ping = round((time.time() - ping_start) * 1000)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    panel = (
        "╔════════════════════════╗\n"
        "   🎧 𝙋𝙄 𝙈𝙐𝙕𝙄𝙆 𝘽𝙊𝙏   \n"
        "╚════════════════════════╝\n\n"
        f"🗓️ **Başlangıç:** `{start_date}`\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"📡 **Ping:** `{ping} ms`\n"
        f"🧠 **CPU:** %{cpu} | **RAM:** %{ram}\n"
        f"🎵 **SoundCloud:** {sc_stat}\n"
        f"🗄️ **PostgreSQL:** `OK`\n"
        f"👤 **Kullanıcılar:** `{users}`\n"
        f"💬 **Gruplar:** `{chats}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 **Geliştirici:** `@dnztrmnn`\n"
    )

    try:
        await client.send_message(config.STATS_CHANNEL_ID, panel)
        await message.reply("✅ **Durum raporu log kanalına gönderildi.**")
    except Exception as e:
        await message.reply(f"⚠️ **Log kanalına gönderilemedi!** (Bot kanalda yönetici mi?)\n\n🔎 *Hata:* `{e}`")
