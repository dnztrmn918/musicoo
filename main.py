import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from call import call_py, assistant, get_video_info, play_music, queue

# DÜZELTME: İki Client'ın çakışmaması için ":memory:" yerine "ZirveBot" kullanıyoruz.
app = Client(
    "ZirveBot", 
    api_id=Config.API_ID, 
    api_hash=Config.API_HASH, 
    bot_token=Config.BOT_TOKEN
)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    print(f"📥 BİRİ BOTA MESAJ ATTI: {message.from_user.first_name}")
    await message.reply_text(
        f"👋 **Merhaba {message.from_user.mention}!**\n\n🎵 Zirve Müzik botu aktif ve kullanıma hazır.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Gruba Ekle", url=f"https://t.me/{client.me.username}?startgroup=true")]
        ])
    )

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("❌ Lütfen bir şarkı adı yazın.")

    m = await message.reply_text(f"🔍 `{query}` aranıyor...")
    
    info = get_video_info(query)
    
    if not info:
        return await m.edit("❌ Şarkı bulunamadı.")

    success = await play_music(message.chat.id, info)
    
    if success:
        queue.append(info["title"])
        await message.reply_photo(
            photo=info["thumbnail"],
            caption=f"🎵 **Oynatılıyor:** `{info['title']}`\n👤 **İsteyen:** {message.from_user.mention}"
        )
        await m.delete()
    else:
        await m.edit("❌ Sesli sohbet başlatılamadı. Asistanın grupta ve yetkili olduğundan emin olun.")

@app.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_cmd(client, message):
    try:
        await call_py.leave_call(message.chat.id)
        queue.clear()
        await message.reply_text("⏹ **Müzik durduruldu.**")
    except:
        await message.reply_text("❌ Zaten çalan bir şey yok.")

async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    
    # Botun başarılı giriş yaptığını teyit eden log:
    me = await app.get_me()
    print(f"🚀 Başarılı! Çalışan Bot: @{me.username}") 
    print("🚀 Bot ve Asistan başarıyla başlatıldı, mesajlar dinleniyor...")
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot kapatılıyor...")
