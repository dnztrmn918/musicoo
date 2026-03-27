import time
from pyrogram import Client, filters
import config
from database import get_served_chats, get_served_users

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
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
    ping_time += ":".join(time_list)
    return ping_time

@Client.on_message(filters.command("bilgi") & filters.user(config.SUDO_USERS))
async def info_to_channel(client, message):
    m = await message.reply_text("⏳ **Veriler senkronize ediliyor...**")
    
    # main'den verileri güvenli çekiyoruz
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
