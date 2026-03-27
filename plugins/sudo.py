import time
from pyrogram import Client, filters
import config
from database import get_served_chats, get_served_users

@Client.on_message(filters.command("sudoadd") & filters.user(config.SUDO_USERS))
async def add_sudo(client, message):
    if len(message.command) < 2:
        return await message.reply("📖 **Kullanım:** `/sudoadd [ID]`")
    try:
        user_id = int(message.command[1])
        if user_id not in config.SUDO_USERS:
            config.SUDO_USERS.append(user_id)
            await message.reply(f"✅ `{user_id}` Sudo listesine eklendi.")
        else:
            await message.reply("⚠️ Bu kullanıcı zaten Sudo.")
    except:
        await message.reply("❌ Geçerli bir sayısal ID girin.")

@Client.on_message(filters.command("sudosil") & filters.user(config.SUDO_USERS))
async def remove_sudo(client, message):
    if len(message.command) < 2:
        return await message.reply("📖 **Kullanım:** `/sudosil [ID]`")
    try:
        user_id = int(message.command[1])
        if user_id in config.SUDO_USERS:
            config.SUDO_USERS.remove(user_id)
            await message.reply(f"🗑 `{user_id}` Sudo listesinden silindi.")
        else:
            await message.reply("❌ Bu kullanıcı Sudo değil.")
    except: pass

@Client.on_message(filters.command("bilgi") & filters.user(config.SUDO_USERS))
async def info_to_channel(client, message):
    from main import userbot, START_TIME
    all_chats = await get_served_chats()
    all_users = await get_served_users()
    uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - START_TIME))
    
    stats_text = (
        "┌────────────────────┐\n"
        "        SİSTEM İSTATİSTİKLERİ \n"
        "└────────────────────┘\n\n"
        f"🏠 Grup Sayısı ➪ `{len(all_chats)}` \n"
        f"👤 Kullanıcılar ➪ `{len(all_users)}` \n"
        f"🤖 Bot Durumu ➪ `🟢 ÇALIŞIYOR` \n"
        f"🎙️ Asistan ➪ `{'🟢 AKTİF' if userbot.is_connected else '🔴 PASİF'}` \n"
        f"⏳ Uptime ➪ `{uptime}` \n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Powered by @{client.me.username}"
    )
    try:
        await client.send_message(config.STATS_CHANNEL_ID, stats_text)
        await message.reply("✅ İstatistik raporu kanala iletildi.")
    except Exception as e:
        await message.reply(f"❌ Hata: {e}")
