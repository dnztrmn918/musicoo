from pyrogram import Client, filters
import time
import config
from database import add_sudo_user, remove_sudo_user, get_sudo_users, is_sudo, get_served_chats, get_served_users


# ────────────────────────────────────────────────
#  SADECE OWNER YETKİLİ KOMUTLAR
# ────────────────────────────────────────────────
@Client.on_message(filters.command("sudoadd"))
async def sudo_add(client, message):
    uid = message.from_user.id
    if uid != config.SUDO_OWNER_ID:
        return await message.reply("⛔ **Bu yetki sadece bot sahibine aittir.**")

    target = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else (int(message.command[1]) if len(message.command) > 1 else None)
    )

    if not target:
        return await message.reply("📎 Kullanıcı ID belirtin veya bir mesaja yanıtlayın.")
    if target == config.SUDO_OWNER_ID:
        return await message.reply("⚠️ Sahibin zaten sudo yetkisi var.")

    await add_sudo_user(target)
    await message.reply(f"✅ `{target}` **sudo listesine eklendi.**")


@Client.on_message(filters.command("sudosil"))
async def sudo_del(client, message):
    uid = message.from_user.id
    if uid != config.SUDO_OWNER_ID:
        return await message.reply("⛔ **Bu yetki sadece bot sahibine aittir.**")

    target = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else (int(message.command[1]) if len(message.command) > 1 else None)
    )
    if not target:
        return await message.reply("📎 Kullanıcı ID belirtin veya bir mesaja yanıtlayın.")
    if target == config.SUDO_OWNER_ID:
        return await message.reply("⚠️ Owner silinemez.")

    await remove_sudo_user(target)
    await message.reply(f"🗑 `{target}` **sudo listesinden çıkarıldı.**")


# ────────────────────────────────────────────────
#  SUDO / STAT KOMUTLARI
# ────────────────────────────────────────────────
@Client.on_message(filters.command("sudolist"))
async def sudo_list(client, message):
    if not await is_sudo(message.from_user.id):
        return
    sudos = await get_sudo_users()
    text = "👑 **Sudo Kullanıcıları**\n\n"
    for i, uid in enumerate(sudos, start=1):
        text += f"`{i}.` `{uid}`\n"
    await message.reply(text)


@Client.on_message(filters.command("bilgi"))
async def bot_info(client, message):
    if not await is_sudo(message.from_user.id):
        return await message.reply("⛔ **Yalnızca SUDO kullanıcıları erişebilir.**")

    import main
    from psutil import cpu_percent, virtual_memory
    import requests

    uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - main.START_TIME))
    ping_start = time.time()
    try:
        sc = requests.get("[soundcloud.com](https://soundcloud.com)", timeout=5)
        sc_stat = "🟢 Aktif" if sc.status_code == 200 else "🟡 Yavaş"
    except:
        sc_stat = "🔴 Kapalı"

    ping = round((time.time() - ping_start) * 1000)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    cpu = cpu_percent()
    ram = virtual_memory().percent

    panel = (
        "╔════════════════════════╗\n"
        "   🎧 𝙋𝙄 𝙈𝙐𝙕𝙄𝙆 𝘽𝙊𝙏   \n"
        "╚════════════════════════╝\n\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"📡 **Ping:** `{ping} ms`\n"
        f"🧠 **CPU:** %{cpu} | **RAM:** %{ram}\n"
        f"🎵 **SoundCloud:** {sc_stat}\n"
        f"🗄️ **PostgreSQL:** `OK`\n"
        f"👤 **Kullanıcılar:** `{users}`\n"
        f"💬 **Gruplar:** `{chats}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧩 **Bot sahibi:** `{config.SUDO_OWNER_ID}`\n"
    )

    await client.send_message(config.STATS_CHANNEL_ID, panel)
    await message.reply("✅ **Durum raporu kanala gönderildi.**")
