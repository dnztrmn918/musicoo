import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
import player # player.py dosyasını içe aktarıyoruz

# Bot ve Asistanı Başlatma
bot = Client(
    "pi_music_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

call = PyTgCalls(bot)

# BURASI ÇOK ÖNEMLİ: Player dosyasındaki 'call' değişkenini bağlıyoruz
player.call = call 

async def main():
    print("İstemciler başlatılıyor...")
    await bot.start()
    await call.start()
    print("✅ Pi-Müzik Botu Başarıyla Çalışıyor!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
