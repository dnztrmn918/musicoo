import asyncio
import time
import sys
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config
from database import init_db, add_sudo_user

# ─── KOYEB KANDIRMA SERVİSİ (SAHTE WEB SUNUCUSU) ───
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot sapasaglam ayakta!")

def run_dummy_server():
    try:
        # Koyeb genellikle PORT değişkenini atar, yoksa 8080 kullanırız
        port = int(os.environ.get("PORT", 8080))
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, DummyHandler)
        print(f"🌐 Sahte web sunucusu {port} portunda başlatıldı...")
        httpd.serve_forever()
    except Exception as e:
        print(f"⚠️ Web server hatası: {e}")

# Arka planda sunucuyu başlat (Botun çalışmasını engellemez)
threading.Thread(target=run_dummy_server, daemon=True).start()
# ───────────────────────────────────────────────────

START_TIME = time.time()

# 🛡️ GÜVENLİK KONTROLÜ
if not config.SESSION:
    print("❌ KRİTİK HATA: SESSION değişkeni boş!")
    sys.exit(1)

bot = Client("pi_music_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, plugins=dict(root="plugins"))
userbot = Client("pi_assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION, in_memory=True)

call = PyTgCalls(userbot)

# Bot ve Asistanı player dosyasına gönderiyoruz
import player
player.call = call
player.userbot = userbot
player.bot = bot

@call.on_stream_end()
async def stream_end(client, update):
    from plugins.events import on_stream_end_handler
    # Olası hatalarda botun tamamen kapanmasını önlemek için try-except
    try:
        await on_stream_end_handler(client, update)
    except Exception as e:
        print(f"⚠️ Stream End Error: {e}")

async def main():
    print("🚀 Sistem Ayağa Kaldırılıyor...")
    await init_db()
    await add_sudo_user(config.SUDO_OWNER_ID)

    print("🤖 Ana Bot başlatılıyor...")
    await bot.start()
    
    print("👤 Asistan motoru ateşleniyor...")
    try:
        await userbot.start()
        # KRİTİK EKSİK: Asistanın sisteme oturması için 5 saniye bekleme süresi
        await asyncio.sleep(5) 
    except Exception as e:
        print(f"❌ ASİSTAN BAŞLATILAMADI: {e}")
        sys.exit(1)

    print("📞 Ses Motoru başlatılıyor...")
    # Pytgcalls başlatılırken hata payını minimize ediyoruz
    await call.start()

    print("✅ Bot ve Asistan başarıyla aktif edildi!")
    await idle()
    
    # Kapanışta temizlik
    try:
        await bot.stop()
        await userbot.stop()
    except:
        pass

if __name__ == "__main__":
    # Döngüyü daha güvenli bir şekilde çalıştırıyoruz
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
