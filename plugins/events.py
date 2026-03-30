import asyncio
import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_chat, is_sudo
import player
import config

# 🔥 ÇÖKME HATASINI GİDEREN KISIM: START_TIME artık doğrudan burada hesaplanıyor.
# "from main import START_TIME" satırı silindi.
START_TIME = time.time()
active_voice_chats = {}

def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h} saat, {m} dakika"
    elif m > 0: return f"{m} dakika, {s} sn"
    return f"{s} saniye"

# --- BİLGİ KOMUTU (SADECE SUDO) ---
@Client.on_message(filters.command(["bilgi", "info"]))
async def system_info(client, message: Message):
    if not await is_sudo(message.from_user.id): 
        return await message.reply("❌ **Üzgünüm, bu komut için yetkiniz bulunmamakta. Lütfen geliştirici ile görüşün.**")
    
    m = await message.reply("⚙️ Sistem verileri toplanıyor...")
    uptime = get_readable_time(int(time.time() - START_TIME))
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=0.5)
    
    text = (
        f"📊 **Pi Müzik Sistem Bilgisi**\n\n"
        f"⏱ **Aktiflik Süresi:** `{uptime}`\n"
        f"💾 **RAM Kullanımı:** `% {ram}`\n"
        f"🧠 **CPU Kullanımı:** `% {cpu}`\n"
        f"🌐 **Bağlantı:** `Aktif`\n"
        f"🐘 **Veritabanı:** `PostgreSQL Aktif`\n"
        f"📞 **Aktif Sesli Sohbet:** `{len(player.music_queue)}`\n"
        f"🤖 **Asistan Durumu:** `Bağlı`"
    )
    
    button = InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/dnztrmnn")]])
    
    if hasattr(config, 'LOG_CHANNEL_ID') and config.LOG_CHANNEL_ID:
        try:
            await client.send_message(config.LOG_CHANNEL_ID, text, reply_markup=button)
            await m.edit("✅ **Sistem bilgileri Log Kanalına gönderildi.**")
        except Exception as e:
            await m.edit(f"❌ Log kanalına gönderilemedi. Hata: `{e}`\n\n{text}")
    else:
        await m.edit(text, reply_markup=button)

# --- DURUM KOMUTU ---
@Client.on_message(filters.command(["durum", "ping"]) & filters.group)
async def ping_status(client, message: Message):
    start = time.time()
    m = await message.reply("Gecikme ölçülüyor...")
    ping = (time.time() - start) * 1000
    
    ram = psutil.virtual_memory().percent
    text = (
        f"🏓 **Ping:** `{ping:.2f} ms`\n"
        f"💾 **RAM:** `% {ram}`\n"
        f"🤖 **Asistan:** `Hazır`"
    )
    await m.edit(text)

@Client.on_message(filters.new_chat_members)
async def welcome_bot(client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await add_served_chat(message.chat.id)
            await message.reply_text(
                f"✨ **Merhaba! Ben {client.me.mention}**\n\n"
                "🎵 Sesli sohbetlerde yüksek kalite müzik ve gelişmiş etiketleme için buradayım.\n\n"
                "🚀 **Başlamak için:** `/play [şarkı adı]`\n"
                "🛠 **Tüm komutlar:** `/yardim`"
            )

@Client.on_message(filters.video_chat_started)
async def video_chat_started(client, message: Message):
    active_voice_chats[message.chat.id] = time.time()
    await message.reply_text("🔔 **Sesli Sohbet Başlatıldı!**\nMüzik açmak için `/play` yazabilirsiniz.")

@Client.on_message(filters.video_chat_ended)
async def video_chat_ended(client, message: Message):
    chat_id = message.chat.id
    player.clear_entire_queue(chat_id)
    try: 
        await player.call.leave_call(chat_id)
    except: 
        pass
    
    if chat_id in active_voice_chats:
        start_time = active_voice_chats.pop(chat_id)
        duration = get_readable_time(int(time.time() - start_time))
        final_msg = f"🔇 **Sesli sohbet sonlandırıldı.**\n⏱ **Sohbet toplam `{duration}` sürdü.**"
    else:
        final_msg = "🔇 **Sesli sohbet sonlandırıldı.**"
        
    await message.reply_text(final_msg)
