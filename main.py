import asyncio
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config

# --- KOYEB KANDIRMA SERVİSİ ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot Aktif!")

def run_dummy_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        httpd = HTTPServer(('0.0.0.0', port), DummyHandler)
        httpd.serve_forever()
    except: pass

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT İSTEMCİLERİ ---
bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=dict(root="plugins"))
userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION, in_memory=True)
call = PyTgCalls(userbot)

async def main():
    print("🚀 Sistem başlatılıyor...")
    
    # 1. Asistanı Başlat
    await userbot.start()
    
    # 2. Ses Motorunu Başlat
    await call.start()
    print("📞 Ses Motoru (v2.2.11) hazır!")

    # 3. PLAYER'I CANLI OLARAK EŞİTLE (Hata Çözücü Nokta)
    import player
    player.call = call
    player.userbot = userbot
    player.bot = bot
    
    # 4. En son Botu Başlat
    await bot.start()
    print("✅ Her şey hazır, bot yayında!")
    
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
