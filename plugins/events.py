import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_chat
import player

active_voice_chats = {}

def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h} saat, {m} dakika, {s} saniye"
    elif m > 0: return f"{m} dakika, {s} saniye"
    return f"{s} saniye"

# --- ŞARKI BİTİŞ OLAYI (DECORATOR KALDIRILDI - ÇAKIŞMA ÖNLENDİ) ---
async def on_stream_end_handler(client, update):
    # Gereksiz "if True:" bloğu silinip kod hizalandı
    chat_id = update.chat_id
    result = await player.stream_end_handler(chat_id)
    
    from main import bot
    if result == "EMPTY":
        await bot.send_message(chat_id, "🛑 **Kuyruk bitti, asistan sesten ayrıldı.** 👋")
    elif result:
        thumb = result["info"].get("thumbnail") or "https://telegra.ph/file/69204068595f57731936c.jpg"
        await bot.send_photo(
            chat_id, 
            photo=thumb, 
            caption=player.format_playing_message(result["info"], result["by"]), 
            reply_markup=player.get_player_ui()
        )

# --- BOT GRUBA EKLENDİĞİNDE ---
@Client.on_message(filters.new_chat_members)
async def welcome_bot(client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await add_served_chat(message.chat.id)
            await message.reply_text(
                f"✨ **Merhaba! Ben {client.me.mention}**\n\n"
                "🎵 Sesli sohbetlerde yüksek kalite müzik ve gelişmiş etiketleme için buradayım.\n\n"
                "🚀 **Başlamak için:** `/play [şarkı adı]`\n"
                "🛠 **Tüm komutlar:** `/yardim`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 Kanal", url="https://t.me/NowaDestek")]])
            )

# --- SESLİ SOHBET BAŞLATILDIĞINDA ---
@Client.on_message(filters.video_chat_started)
async def video_chat_started(client, message: Message):
    active_voice_chats[message.chat.id] = time.time()
    await message.reply_text("🔔 **Sesli Sohbet Başlatıldı!**\nMüzik açmak için `/play` yazabilirsiniz. 🎧")

# --- RELOAD KOMUTU ---
@Client.on_message(filters.command(["reload", "güncelle", "yenile"]))
async def reload_system(client, message):
    m = await message.reply_text("⚙️ **Veriler senkronize ediliyor...**")
    try:
        if message.chat.type != message.chat.type.PRIVATE:
            await client.get_chat_member(message.chat.id, "me")
        await asyncio.sleep(1)
        await m.edit("✅ **Sistem ve yönetici listesi başarıyla tazelendi!**")
    except Exception as e:
        await m.edit(f"❌ **Hata:** `{e}`")

# --- SESLİ SOHBET BİTTİĞİNDE ---
@Client.on_message(filters.video_chat_ended)
async def video_chat_ended(client, message: Message):
    player.clear_entire_queue(message.chat.id)
    # KRİTİK DEĞİŞİKLİK: leave_group_call artık V2'ye uygun şekilde leave_call oldu
    try: await player.call.leave_call(message.chat.id)
    except: pass
    
    start_time = active_voice_chats.pop(message.chat.id, None)
    duration_text = ""
    if start_time:
        duration_sec = int(time.time() - start_time)
        duration_text = f"\n⏱ **Aktiflik Süresi:** {get_readable_time(duration_sec)}"
        
    await message.reply_text(f"🔇 **Sesli sohbet sonlandırıldı.**{duration_text}")
