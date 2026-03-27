import player
import asyncio
from pytgcalls.types.stream import StreamAudioEnded
from pyrogram.errors import UserAlreadyParticipant, FloodWait

async def on_stream_end_handler(client, update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        from main import bot # Fonksiyon içi import
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

async def assistant_join(client, chat_id):
    from main import userbot
    try:
        me = await userbot.get_me()
        await client.get_chat_member(chat_id, me.id)
        return True
    except:
        try:
            invitelink = await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(invitelink)
            return True
        except UserAlreadyParticipant:
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await assistant_join(client, chat_id)
        except Exception:
            return False
