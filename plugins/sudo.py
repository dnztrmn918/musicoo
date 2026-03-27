import time
from pyrogram import Client, filters
import config
from database import get_served_chats, get_served_users

def get_readable_time(seconds: int) -> str:
    count, ping_time, time_list = 0, "", []
    time_suffix_list = ["s", "m", "h", "d"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4: ping_time += time_list.pop() + ", "
    time_list.reverse()
    return ping_time + ":".join(time_list)

@Client.on_message(filters.command("sudoadd") & filters.user(config.SUDO_USERS))
async def add_sudo(client, message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    
    if not user_id:
        return await message.reply("📖 **Kullanım:** Bir mesajı yanıtlayın veya ID yazın.")

    if user_id not in config.SUDO_USERS:
        config.SUDO_USERS.append(user_id)
        await message.reply(f"✅ `{user_id}` Sudo listesine eklendi.")
    else:
        await message.reply("⚠️ Bu kullanıcı zaten Sudo.")

@Client.on_message(filters.command("sudosil") & filters.user(config.SUDO_USERS))
async def remove_sudo(client, message):
    user_id = int(message.command[1]) if len(message.command) > 1 else None
    if message.reply_to_message: user_id = message.reply_to_message.from_user.id
    
    if user_id in config.SUDO_USERS:
        config.SUDO_USERS.remove(user_id)
        await message.reply(f"🗑 `{user_id}` Sudo listesinden çıkarıldı.")
    else:
        await message.reply("❌ Bu kullanıcı Sudo değil.")

@Client.on_message(filters.command("bilgi") & filters.user(config.SUDO_USERS))
async def info_to_channel(client, message):
    m = await message.reply_text("⏳ **Veriler senkronize ediliyor...**")
    import main
    all_chats = await get_served_chats()
    all_users = await get_served_users()
    uptime = get_readable_time(int(time.time() - main.START_TIME))
    ass_status = "🟢 AKTİF" if main.userbot.is_connected else "🔴 PASİF"
    
    stats_text = (
        "┌────────────────────┐\n"
        "        SİSTEM İSTATİSTİKLERİ \n"
        "└────────────────────┘\n\n"
        f"🏠 Grup Sayısı ➪ `{len(all_chats)}` \n"
        f"👤 Kullanıcılar ➪ `{len(all_users)}` \n"
        f"🤖 Bot Durumu ➪ `🟢 ÇALIŞIYOR` \n"
        f"🎙️ Asistan ➪ `{ass_status}` \n"
        f"⏳ Uptime ➪ `{uptime}` \n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 Bağlantı ➪ `Sorunsuz` \n"
        f"📅 Tarih ➪ `{time.strftime('%d/%m/%Y')}` \n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Powered by @{client.me.username}"
    )
    
    try:
        await client.send_message(config.STATS_CHANNEL_ID, stats_text)
        await m.edit("✅ **İstatistik raporu kanala iletildi.**")
    except Exception as e:
        await m.edit(f"❌ **Hata:** `{e}`")
