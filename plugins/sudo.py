import time
from pyrogram import Client, filters
import config
from database import get_served_chats, get_served_users

@Client.on_message(filters.command("sudoadd") & filters.user(config.SUDO_USERS))
async def add_sudo(client, message):
    # Yanıtlanan mesajdan veya ID'den kullanıcı çekme
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else (int(message.command[1]) if len(message.command) > 1 else None)
    
    if not user_id:
        return await message.reply("📖 **Kullanım:** Bir mesajı yanıtlayın veya ID yazın.")

    if user_id not in config.SUDO_USERS:
        config.SUDO_USERS.append(user_id)
        await message.reply(f"✅ `{user_id}` başarıyla Sudo listesine eklendi.")
    else:
        await message.reply("⚠️ Bu kullanıcı zaten Sudo listesinde.")

@Client.on_message(filters.command("sudosil") & filters.user(config.SUDO_USERS))
async def remove_sudo(client, message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else (int(message.command[1]) if len(message.command) > 1 else None)
    
    if user_id in config.SUDO_USERS:
        config.SUDO_USERS.remove(user_id)
        await message.reply(f"🗑 `{user_id}` Sudo listesinden çıkarıldı.")
    else:
        await message.reply("❌ Bu kullanıcı Sudo değil.")

@Client.on_message(filters.command("bilgi") & filters.user(config.SUDO_USERS))
async def info_to_channel(client, message):
    import main # START_TIME hatasını önlemek için burada çekiyoruz
    uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - main.START_TIME))
    all_chats = await get_served_chats()
    
    stats_text = (
        "┌────────────────────┐\n"
        "        SİSTEM İSTATİSTİKLERİ \n"
        "└────────────────────┘\n\n"
        f"🏠 Toplam Grup ➪ `{len(all_chats)}` \n"
        f"🎙️ Asistan ➪ `{'🟢 AKTİF' if main.userbot.is_connected else '🔴 PASİF'}` \n"
        f"⏳ Uptime ➪ `{uptime}` \n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Powered by @{client.me.username}"
    )
    try:
        await client.send_message(config.STATS_CHANNEL_ID, stats_text)
        await message.reply("✅ İstatistik raporu kanala iletildi.")
    except Exception as e:
        await message.reply(f"❌ Rapor iletilemedi: `{e}`")
