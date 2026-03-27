import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types.stream import StreamAudioEnded
from database import add_served_chat
import player

# --- ŞARKI BİTİŞ OLAYI ---
async def on_stream_end_handler(client, update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        from main import bot
        if result == "EMPTY":
            await bot.send_message(chat_id, "ℹ️ **Kuyruk bitti, yayın sonlandırıldı.** 👋")
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
    await message.reply_text("🔔 **Sesli Sohbet Başlatıldı!**\nMüzik açmak için `/play` yazabilirsiniz. 🎧")

# --- RELOAD KOMUTU (SİSTEM YENİLEME) ---
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

# --- SESLİ SOHBET BİTTİĞİNDE TEMİZLİK ---
@Client.on_message(filters.video_chat_ended)
async def video_chat_ended(client, message: Message):
    player.music_queue.pop(message.chat.id, None)
    try: await player.call.leave_group_call(message.chat.id)
    except: pass
