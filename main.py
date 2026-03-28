import asyncio
import time
import sys
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
from database import init_db, add_sudo_user

START_TIME = time.time()

if not config.SESSION:
    print("❌ KRİTİK HATA: SESSION değişkeni boş!")
    sys.exit(1)

# plugins root tanımlamasını koruduk
bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=dict(root="plugins"))
userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION, in_memory=True)

call = PyTgCalls(userbot)

# Player entegrasyonu
import player
player.call = call
player.userbot = userbot
player.bot = bot

@call.on_stream_end()
async def stream_end(client, update):
    from plugins.events import on_stream_end_handler
    # Bağlantı kopmalarına karşı güvenli çalıştırma
    try:
        await on_stream_end_handler(client, update)
    except Exception as e:
        print(f"❌ Stream End Error: {e}")

async def main():
    print("🚀 Sistem Ayağa Kaldırılıyor...")
    await init_db()
    await add_sudo_user(config.SUDO_OWNER_ID)

    print("🤖 Ana Bot başlatılıyor...")
    await bot.start()
    
    print("👤 Asistan motoru ateşleniyor...")
    try:
        await userbot.start()
    except Exception as e:
        print(f"❌ ASİSTAN BAŞLATILAMADI: {e}")
        sys.exit(1)

    print("📞 Ses Motoru başlatılıyor...")
    await call.start()
    
    # KRİTİK: Sistemin oturması için kısa bir es (ConnectionError çözümü)
    await asyncio.sleep(2)

    print("✅ Bot ve Asistan başarıyla aktif edildi!")
    await idle()
    
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    # Döngü yönetimini daha stabil hale getirdik
    asyncio.get_event_loop().run_until_complete(main())
