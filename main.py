import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
import config
import player 

bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=dict(root="plugins"))

if config.SESSION:
    userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION)
    call = PyTgCalls(userbot) 
else:
    print("❌ KRİTİK HATA: SESSION kodu bulunamadı!")
    call = PyTgCalls(bot)

player.call = call 

# ŞARKI BİTİNCE OTOMATİK ÇALIŞAN TETİKLEYİCİ
@call.on_stream_end()
async def on_stream_end(client, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        if result == "EMPTY":
            await bot.send_message(chat_id, "ℹ️ Kuyrukta herhangi bir parça yok, asistan sesli sohbetten ayrılıyor.")
        elif result:
            await bot.send_message(
                chat_id,
                player.format_playing_message(result["info"], result["by"]),
                reply_markup=player.get_player_ui()
            )

async def main():
    print("İstemciler başlatılıyor...")
    await bot.start()
    if config.SESSION:
        try:
            await userbot.start()
            print("✅ Asistan Bağlandı!")
        except Exception as e:
            print(f"❌ Asistan Hatası: {e}")
    await call.start()
    print("✅ Pi-Müzik Botu Çalışıyor!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
