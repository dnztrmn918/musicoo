import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN, SESSION
import player

bot = Client(
    "PiMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "plugins"} 
)

user_app = Client(
    "PiMusicUser",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

call = PyTgCalls(user_app)
player.call = call

async def main():
    print("İstemciler başlatılıyor...")
    await bot.start()
    await user_app.start()
    await call.start()
    print("✅ Pi-Müzik Botu Başarıyla Çalışıyor!")
    
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
