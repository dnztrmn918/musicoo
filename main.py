import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN, SESSION
import player

# Pyrogram Bot İstemcisi (plugins klasörü olarak ana dizini okur, start ve play dosyalarını otomatik tanır)
bot = Client(
    "PiMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root=".")
)

# Pyrogram Userbot İstemcisi (Sesli sohbete katılmak için gerekli)
user_app = Client(
    "PiMusicUser",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

# PyTgCalls Başlatma
call = PyTgCalls(user_app)
player.call = call # Oynatıcı dosyasına call objesini aktarıyoruz

async def main():
    print("İstemciler başlatılıyor...")
    await bot.start()
    await user_app.start()
    await call.start()
    print("✅ Pi-Müzik Botu Başarıyla Çalışıyor!")
    
    # Botun kapanmasını engellemek için idle() kullanıyoruz
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
