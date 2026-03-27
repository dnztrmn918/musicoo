import asyncio
import time
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config, player 
from database import init_db

# CRITICAL: ImportError'u önlemek için START_TIME en üstte tanımlanmalı
START_TIME = time.time() 

bot = Client(
    "pi_music_bot", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.BOT_TOKEN, 
    plugins=dict(root="plugins")
)

userbot = Client(
    "pi_assistant", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    session_string=config.SESSION
)

call = PyTgCalls(userbot)
player.call = call 

# Olay yöneticisini events.py dosyasına bağla
@call.on_stream_end()
async def stream_end_handler(client, update):
    from plugins.events import on_stream_end_handler
    await on_stream_end_handler(client, update)

async def main():
    print("🚀 Sistem başlatılıyor...")
    await init_db()
    await bot.start()
    await userbot.start()
    await call.start()
    
    try:
        await bot.send_message(config.LOG_GROUP_ID, "✅ **Nowa-Müzik Sistemi ve Asistan Çevrimiçi!**")
    except: pass
    
    print("✅ Bot ve Asistan Sorunsuz Başlatıldı!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
