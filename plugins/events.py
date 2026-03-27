from pyrogram import Client, filters
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
import player

@Client.on_message(filters.video_chat_started)
async def vc_started(client, message):
    await message.reply_text("✨ **Sesli Sohbet Başarıyla Başlatıldı!**\n\n🎵 Müzik yayını yapılmaya hazır. `/play` komutu ile kulakların pasını silebiliriz! 🎧")

@Client.on_message(filters.new_chat_members)
async def welcome_bot(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            return await message.reply_text(
                "👋 **Beni gruba aldığın için teşekkürler!**\n\n"
                "🎵 Yetki vererek kullanım adımlarını takip edip kullanmaya başlayabilirsiniz.\n"
                "🛡️ Lütfen 'Mesajları Sil' ve 'Sesli Sohbet Yönet' yetkilerimi verin! ✨"
            )

async def on_stream_end_handler(client, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        # Hata Çözümü: main'den bot çekmek yerine başlatılmış olan client'ı buluyoruz
        from main import bot 
        
        if bot.is_connected: # Bağlantı kontrolü eklendi
            if result == "EMPTY":
                await bot.send_message(chat_id, "ℹ️ **Kuyrukta herhangi bir parça yok, asistan sesli sohbetten ayrılıyor.** 👋")
            elif result:
                # SoundCloud'da bazen thumbnail gelmeyebilir, kontrol ekledik
                thumb = result["info"].get("thumbnail") or "https://telegra.ph/file/69204068595f57731936c.jpg"
                await bot.send_photo(
                    chat_id,
                    photo=thumb,
                    caption=player.format_playing_message(result["info"], result["by"]),
                    reply_markup=player.get_player_ui()
                )
