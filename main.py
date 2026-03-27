import asyncio
import time
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
from database import init_db, add_sudo_user, get_sudo_users

START_TIME = time.time()

bot = Client(
    "pi_music_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

userbot = Client(
    "pi_assistant",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION
)

call = PyTgCalls(userbot)

# player modülüne call nesnesini aktar
import player
player.call = call


@call.on_stream_end()
async def stream_end(client, update):
    from plugins.events import on_stream_end_handler
    await on_stream_end_handler(client, update)


async def main():
    print("🚀 Başlatılıyor...")
    await init_db()

    # owner'ı sudo'ya ekle (tabloya garanti olsun)
    await add_sudo_user(config.SUDO_OWNER_ID)

    await bot.start()
    await userbot.start()
    await call.start()

    print("✅ Bot ve Asistan aktif!")

    # Log grubuna aktif mesajı
    uptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        await bot.send_message(
            config.LOG_GROUP_ID,
            f"✅ **Pi Müzik Bot Aktif!**\n\n🕓 Başlangıç: `{uptime}`\n"
            f"📡 PostgreSQL Bağlantısı: `OK`\n"
            f"🎧 Asistan: `{'AKTİF' if userbot.is_connected else 'PASİF'}`",
        )
    except Exception as e:
        print(f"⚠️ Log mesajı gönderilemedi: {e}")

    await idle()

    await bot.stop()
    await userbot.stop()
    print("💤 Sistem kapandı.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
