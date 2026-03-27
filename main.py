import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
import player 
from database import init_db
from plugins.events import on_stream_end_handler # Yeni import

# Ana Bot
bot = Client(
    "pi_music_bot", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.BOT_TOKEN, 
    plugins=dict(root="plugins")
)

# Asistan
userbot = Client(
    "pi_assistant", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    session_string=config.SESSION
)

call = PyTgCalls(userbot)
player.call = call 

# Şarkı bitişini events.py'deki fonksiyona yönlendiriyoruz
@call.on_stream_end()
async def stream_end(client, update):
    await on_stream_end_handler(client, update)

async def main():
    print("🚀 Sistem başlatılıyor...")
    await init_db()
    await bot.start()
    await userbot.start()
    await call.start()
    print("✅ Pi-Müzik Botu, Asistan ve Olay Yöneticileri Aktif!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
