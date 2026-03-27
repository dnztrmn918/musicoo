import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config, player 
from database import init_db

# Bot Nesnesi
bot = Client(
    "pi_music_bot", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.BOT_TOKEN, 
    plugins=dict(root="plugins")
)

# Asistan Nesnesi
userbot = Client(
    "pi_assistant", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    session_string=config.SESSION
)

call = PyTgCalls(userbot)
player.call = call 

# Şarkı bittiğinde tetiklenen mekanizma
@call.on_stream_end()
async def stream_end_handler(client, update):
    from pytgcalls.types.stream import StreamAudioEnded
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        # Kuyruk işlemlerini güvenli bir try-except bloğuna alıyoruz
        try:
            result = await player.stream_end_handler(chat_id)
            
            # bot nesnesinin başlatıldığından ve bağlı olduğundan emin ol
            if bot and bot.is_connected:
                if result == "EMPTY":
                    await bot.send_message(chat_id, "ℹ️ **Kuyruk bitti, asistan ayrılıyor.** 👋")
                elif result:
                    await bot.send_message(
                        chat_id, 
                        player.format_playing_message(result["info"], result["by"]), 
                        reply_markup=player.get_player_ui()
                    )
        except Exception as e:
            print(f"Stream End Hatası: {e}")

async def main():
    print("🚀 Sistem başlatılıyor...")
    await init_db()
    await bot.start()
    await userbot.start()
    await call.start()
    print("✅ Pi-Müzik Botu ve Asistan Sorunsuz Başlatıldı!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
