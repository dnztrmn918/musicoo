from pyrogram import Client, filters
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
import player

# SESLİ SOHBET BAŞLATILDIĞINDA MESAJ GÖNDERME
@Client.on_message(filters.video_chat_started)
async def vc_started(client, message):
    await message.reply_text(
        "✅ **Sesli Sohbet başarıyla başlatıldı!**\n"
        "Müzik yayını yapılmaya hazır. `/play` komutu ile başlayabilirsiniz."
    )

# BOT GRUBA İLK ALINDIĞINDA HOŞ GELDİN MESAJI
@Client.on_message(filters.new_chat_members)
async def welcome_bot(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            return await message.reply_text(
                "👋 **Beni gruba aldığın için teşekkürler!**\n\n"
                "🎵 Sorunsuz çalışmam için bana 'Mesajları Sil' ve 'Sesli Sohbetleri Yönet' yetkisi vermeyi unutmayın.\n"
                "📖 Kullanım adımları için `/start` veya `/help` yazabilirsiniz."
            )

# ŞARKI BİTİŞİNİ YÖNETEN FONKSİYON (Bunu main.py'den çağıracağız)
async def on_stream_end_handler(client, update: Update):
    if isinstance(update, StreamAudioEnded):
        result = await player.stream_end_handler(update.chat_id)
        if result == "EMPTY":
            # Botun ana objesine (client) erişmek için main'deki bot objesini kullanır
            from main import bot
            await bot.send_message(update.chat_id, "ℹ️ Kuyrukta parça yok, asistan ayrılıyor.")
        elif result:
            from main import bot
            await bot.send_message(
                update.chat_id, 
                player.format_playing_message(result["info"], result["by"]), 
                reply_markup=player.get_player_ui()
            )
