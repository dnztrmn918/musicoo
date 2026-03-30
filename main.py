import asyncio
import os
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Update

# main.py dosyanın en üstüne ekle (events.py artık buradan okuyacak)
START_TIME = time.time()

sys.path.append('.')
import config
import player 

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

# 🔥 ÇÖKME HATASI GİDERİLDİ: ptg_filters yerine güvenli if kontrolü kullanıldı
@call.on_update()
async def global_update_handler(client, update: Update):
    # Eğer update mesajında şarkının bittiğine dair bir sinyal varsa yakala
    update_str = str(update).lower()
    if "stream_end" in update_str or "finished" in update_str or "streamaudioended" in update_str:
        try:
            chat_id = update.chat_id
            print(f"✅ Şarkı bitti, otomatiğe geçiliyor. Chat: {chat_id}")
            await player.stream_end_handler(chat_id, action="auto")
        except Exception as e:
            print(f"⚠️ Otomatik geçişte ufak bir hata: {e}")

async def main():
    print("🚀 Pi Müzik Sistem başlatılıyor...")
    try:
        from database import init_db
        await init_db()
    except Exception as e: print(f"⚠️ Veritabanı uyarısı: {e}")

    await userbot.start()
    await bot.start()
    await call.start()
    
    player.call = call
    player.userbot = userbot
    player.bot = bot

    me = await bot.get_me()
    print(f"✅ Bot (@{me.username}) başarıyla aktif edildi! Komutlar dinleniyor...")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try: loop.run_until_complete(main())
    except Exception as err: print(f"❌ Ana döngü hatası: {err}")
