import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types.stream import StreamAudioEnded
from database import add_served_chat
import player
import config

# --- 1. ŞARKI BİTİŞ OLAYI ---
async def on_stream_end_handler(client, update):
    """Şarkı bittiğinde sonraki şarkıya geçer veya odayı temizler."""
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        from main import bot # Circular Import önleyici
        if result == "EMPTY":
            await bot.send_message(chat_id, "ℹ️ **Kuyruk bitti, asistan ayrılıyor.** 👋")
        elif result:
            thumb = result["info"].get("thumbnail") or "https://telegra.ph/file/69204068595f57731936c.jpg"
            await bot.send_photo(
                chat_id, 
                photo=thumb, 
                caption=player.format_playing_message(result["info"], result["by"]), 
                reply_markup=player.get_player_ui()
            )

# --- 2. BOT GRUBA EKLENDİĞİNDE KARŞILAMA ---
@Client.on_message(filters.new_chat_members)
async def welcome_bot(client, message: Message):
    """Bot bir gruba eklendiğinde tanıtım mesajı gönderir."""
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await add_served_chat(message.chat.id)
            await message.reply_text(
                f"👋 **Merhaba! Ben {client.me.mention}**\n\n"
                "🎵 Gruplarınızda sesli sohbet üzerinden kesintisiz müzik çalabilirim.\n"
                "🏷️ Gelişmiş etiketleme sistemlerimle grubunuzu canlandırabilirim.\n\n"
                "🛠 **Başlamak için:** `/oynat [şarkı adı]`\n"
                "📚 **Tüm komutlar için:** `/yardim`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Destek Kanalı", url="https://t.me/NowaDestek")]
                ])
            )

# --- 3. SESLİ SOHBET BAŞLATILDIĞINDA BİLGİ ---
@Client.on_message(filters.video_chat_started)
async def video_chat_started(client, message: Message):
    """Grupta sesli sohbet başlatıldığında kullanıcıları bilgilendirir."""
    await message.reply_text(
        "🔔 **Sesli Sohbet Başlatıldı!**\n\n"
        "Müzik dinlemek için `/play` komutunu kullanabilirsiniz.\n"
        "Keyifli vakitler dilerim! 🎧"
    )

# --- 4. RELOAD KOMUTU (SİSTEM YENİLEME) ---
@Client.on_message(filters.command(["reload", "güncelle", "yenile"]))
async def reload_system(client, message):
    """Sistem verilerini ve yönetici listesini tazeler."""
    m = await message.reply_text("⚙️ **Sistem verileri senkronize ediliyor...**")
    try:
        # Grup içindeyse yetkileri tazeler
        if message.chat.type != message.chat.type.PRIVATE:
            await client.get_chat_member(message.chat.id, "me")
        
        await asyncio.sleep(1)
        await m.edit("✅ **Sistem ve yönetici listesi başarıyla tazelendi!**")
    except Exception as e:
        await m.edit(f"❌ **Hata:** `{e}`")

# --- 5. SESLİ SOHBET BİTTİĞİNDE TEMİZLİK (OPSİYONEL) ---
@Client.on_message(filters.video_chat_ended)
async def video_chat_ended(client, message: Message):
    """Sesli sohbet kapandığında kuyruğu temizler."""
    player.music_queue.pop(message.chat.id, None)
    # Asistanın bağlantısını zorla kesmek gerekebilir
    try: await player.call.leave_group_call(message.chat.id)
    except: pass
