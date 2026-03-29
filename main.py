import asyncio
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
import player 

START_TIME = time.time() 

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Aktif!")

def run_dummy_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        httpd = HTTPServer(('0.0.0.0', port), DummyHandler)
        httpd.serve_forever()
    except: pass

threading.Thread(target=run_dummy_server, daemon=True).start()
plugins = dict(root="plugins")

bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=plugins)
userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION)
call = PyTgCalls(userbot)

# 🔥 SÜRÜM ÇAKIŞMASINI ÇÖZEN DİNAMİK DİNLEYİCİ
@call.on_update()
async def global_update_handler(client, update):
    # Objenin adını alarak import veya attribute hatalarını sonsuza dek önlüyoruz
    update_name = update.__class__.__name__
    if update_name in ["StreamAudioEnded", "StreamVideoEnded", "StreamEnd"]:
        await player.stream_end_handler(update.chat_id, action="auto")

async def main():
    print("🚀 Sistem başlatılıyor...")
    try:
        from database import init_db
        await init_db()
    except Exception as e:
        print(f"⚠️ Veritabanı başlatılamadı: {e}")

    await userbot.start()
    await bot.start()
    await call.start()
    
    player.call = call
    player.userbot = userbot
    player.bot = bot

    me = await bot.get_me()
    print(f"✅ Bot (@{me.username}) başarıyla aktif edildi!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try: loop.run_until_complete(main())
    except KeyboardInterrupt: pass
    except Exception as err: print(f"❌ Ana döngü hatası: {err}")
