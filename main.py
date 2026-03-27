import asyncio
import time
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
from database import init_db, add_sudo_user

START_TIME = time.time()

bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=dict(root="plugins"))
userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION)

call = PyTgCalls(userbot)

# HATAYI ÇÖZEN KISIM: Bot ve Asistanı player dosyasına gönderiyoruz
import player
player.call = call
player.userbot = userbot
player.bot = bot

@call.on_stream_end()
async def stream_end(client, update):
    from plugins.events import on_stream_end_handler
    await on_stream_end_handler(client, update)

async def main():
    print("🚀 Başlatılıyor...")
    await init_db()
    await add_sudo_user(config.SUDO_OWNER_ID)

    await bot.start()
    await userbot.start()
    await call.start()

    print("✅ Bot ve Asistan aktif!")
    await idle()
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
