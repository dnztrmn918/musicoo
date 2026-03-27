import asyncio
import time
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config, player 
from database import init_db

# Uptime takibi için değişken (ImportError'u önlemek için en üstte)
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

# Şarkı bittiğinde plugins/assistant.py dosyasındaki fonksiyonu çağırır
@call.on_stream_end()
async def stream_end_handler(client, update):
    from plugins.assistant import on_stream_end_handler
    await on_stream_end_handler(client, update)

async def main():
    print("🚀 Sistem başlatılıyor...")
    await init_db()
    await bot.start()
    await userbot.start()
    await call.start()
    
    try:
        await bot.send_message(config.LOG_GROUP_ID, "✅ **Sistem ve Asistan Başarıyla Çevrimiçi!**")
    except: pass
    
    print("✅ Pi-Müzik Botu ve Asistan Sorunsuz Başlatıldı!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
