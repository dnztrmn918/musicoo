from pyrogram import Client, filters
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
import player
import config

@Client.on_message(filters.video_chat_started)
async def vc_started(client, message):
    await message.reply_text("✨ **Sesli Sohbet Başarıyla Başlatıldı!**")

@Client.on_message(filters.new_chat_members)
async def welcome_and_log(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            await message.reply_text("👋 **Beni gruba aldığın için teşekkürler!**")
            
            if config.LOG_GROUP_ID:
                log_text = (
                    "➕ **Yeni Bir Gruba Eklendim!**\n"
                    f"🏷 **Grup:** `{message.chat.title}`\n"
                    f"🆔 **ID:** `{message.chat.id}`"
                )
                await client.send_message(config.LOG_GROUP_ID, log_text)

async def on_stream_end_handler(client, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        from main import bot 
        if bot.is_connected:
            if result == "EMPTY":
                await bot.send_message(chat_id, "ℹ️ **Kuyruk bitti, asistan ayrılıyor.** 👋")
            elif result:
                thumb = result["info"].get("thumbnail") or "https://telegra.ph/file/69204068595f57731936c.jpg"
                await bot.send_photo(chat_id, photo=thumb, caption=player.format_playing_message(result["info"], result["by"]), reply_markup=player.get_player_ui())
