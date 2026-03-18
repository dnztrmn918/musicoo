import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import Config
from call import call_py, assistant, get_video_info, play_music, queue

app = Client("MusicBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# downloads klasörünü oluştur
if not os.path.exists("downloads"):
    os.makedirs("downloads")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        f"👋 **Merhaba {message.from_user.mention}!**\n\n🎵 Python 3.13 uyumlu güncel müzik botu aktif!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Gruba Ekle", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [InlineKeyboardButton("📢 Kanal", url="https://t.me/KanalLinkiniz")]
        ])
    )

@app.on_message(filters.command("play") & filters.group)
async def play(client, message: Message):
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
        await m.edit("❌ Sesli sohbetin açık olduğundan ve asistanın grupta olduğundan emin olun.")

@app.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_cmd(client, message):
    try:
        await call_py.leave_call(message.chat.id) # Güncel komut: leave_call
        queue.clear()
        await message.reply_text("⏹ **Müzik durduruldu ve asistan ayrıldı.**")
    except:
        await message.reply_text("❌ Zaten çalan bir şey yok.")

# KOMUT: /que (Kuyruk)
@app.on_message(filters.command("que") & filters.group)
async def que_cmd(client, message):
    if not queue:
        return await message.reply_text("🗒 Kuyruk boş.")
    res = "🗒 **Sıradaki Şarkılar:**\n\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(queue)])
    await message.reply_text(res)

# HEM BOTU HEM ASİSTANI AYNI ANDA BAŞLATAN MODERN DÖNGÜ
async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    print("🚀 Bot ve Asistan Python 3.13 üzerinde aktif!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
