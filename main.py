import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
import player 

# 1. Asıl Botu Başlatma (Mesajları okur ve menüleri açar)
bot = Client(
    "pi_music_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

# 2. ASİSTAN (USERBOT) BAĞLANTISI VE KONTROLÜ
if config.SESSION:
    userbot = Client(
        "pi_assistant",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=config.SESSION
    )
    # EUREKA: Ses modülüne Botu değil, ASİSTANI bağlıyoruz!
    call = PyTgCalls(userbot) 
else:
    print("❌ KRİTİK HATA: config.py veya Koyeb üzerinde SESSION (Asistan) kodu bulunamadı!")
    call = PyTgCalls(bot)

player.call = call 

async def main():
    print("İstemciler başlatılıyor...")
    await bot.start()
    
    # Asistanın hesaba giriş yapıp yapmadığını kontrol et
    if config.SESSION:
        try:
            await userbot.start()
            print("✅ Asistan Hesap (Userbot) Başarıyla Telegram'a Bağlandı!")
        except Exception as e:
            print(f"❌ Asistan Bağlantı Hatası: Lütfen SESSION kodunu kontrol et! Hata: {e}")
            
    await call.start()
    print("✅ Pi-Müzik Botu Başarıyla Çalışıyor!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
