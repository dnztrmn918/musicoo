from pyrogram import Client, filters
from config import Config

app = Client(
    "ZirveBot", 
    api_id=Config.API_ID, 
    api_hash=Config.API_HASH, 
    bot_token=Config.BOT_TOKEN,
    in_memory=True
)

@app.on_message(filters.command("start"))
async def start(client, message):
    print(f"📥 BİRİ BOTA MESAJ ATTI: {message.from_user.first_name}", flush=True) 
    await message.reply_text("✅ ZirveBot iletişim kurabiliyor! Altyapı sağlam.")

@app.on_message()
async def catch_all(client, message):
    print(f"🔍 FARKLI BİR MESAJ YAKALANDI: {message.text}", flush=True)

if __name__ == "__main__":
    print("🚀 Test Modu Başlatılıyor...", flush=True)
    app.run()
