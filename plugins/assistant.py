import asyncio
import player
import config
from pyrogram import Client
from pytgcalls.types.stream import StreamAudioEnded

async def on_stream_end_handler(client, update):
    """Şarkı bittiğinde sonraki şarkıya geçer veya odayı temizler."""
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        from main import bot # Fonksiyon içi import ile Circular Import çözüldü
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

async def assistant_join(client: Client, chat_id: int):
    """Asistan grupta yoksa otomatik davet linki ile katılır."""
    from main import userbot
    try:
        # Asistan grupta mı kontrol et
        await client.get_chat_member(chat_id, (await userbot.get_me()).id)
        return True
    except:
        try:
            # Davet linki oluştur ve katıl
            invitelink = await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(invitelink)
            return True
        except Exception as e:
            print(f"Asistan katılım hatası: {e}")
            return False
