import player
from pytgcalls.types.stream import StreamAudioEnded

async def on_stream_end_handler(client, update):
    """Şarkı bittiğinde otomatik sonraki şarkıya geçer."""
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        from main import bot
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
