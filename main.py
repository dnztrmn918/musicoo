import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
import config
import player 
from database import init_db

bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=dict(root="plugins"))
userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION)
call = PyTgCalls(userbot)
player.call = call 

@call.on_stream_end()
async def on_stream_end(client, update: Update):
    if isinstance(update, StreamAudioEnded):
        result = await player.stream_end_handler(update.chat_id)
        if result == "EMPTY":
            await bot.send_message(update.chat_id, "ℹ️ Kuyrukta parça yok, asistan ayrılıyor.")
        elif result:
            await bot.send_message(update.chat_id, player.format_playing_message(result["info"], result["by"]), reply_markup=player.get_player_ui())

async def main():
    await init_db()
    await bot.start()
    await userbot.start()
    await call.start()
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
