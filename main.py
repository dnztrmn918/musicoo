import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import Config
from call import call_py, assistant, get_video_info, play_music, queue, saniyeyi_formatla

app = Client("MusicBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# İndirilen dosyaların geçici olarak tutulacağı klasör
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- KOMUTLAR ---

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/0c325d7b5b5c93c3f97fb.jpg", # Örnek bir kapak görseli
        caption=f"👋 **Merhaba {message.from_user.mention}!**\n\n🎵 Ben gruplarda yüksek kaliteli müzik çalabilen bir botum.\n\n"
                "🔹 Beni kullanmak için grubuna ekle ve yönetici yap.\n"
                "🔹 `/play şarkı adı` yazarak müzik başlatabilirsin.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [InlineKeyboardButton("📢 Resmi Kanal", url="https://t.me/KanalınızınLinki"), # Kendi linkini yaz
             InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/KullanıcıAdınız")] # Kendi linkini yaz
        ])
    )

@app.on_message(filters.command("play") & filters.group)
async def play(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Hata:** Lütfen çalmak istediğiniz şarkının adını yazın!\nÖrn: `/play Sezen Aksu Belalım` ")
    
    query = " ".join(message.command[1:])
    m = await message.reply_text(f"🔍 **'{query}'** aranıyor, lütfen bekleyin...")
    
    # Şarkı bilgilerini al ve indir
    video_info = get_video_info(query)
    
    if not video_info:
        return await m.edit("❌ **Hata:** Şarkı bulunamadı veya bir sorun oluştu.")

    # Kuyruğa ekle (Basit yapı, sadece başlık)
    queue.append(video_info["title"])
    
    # Müziği çalmayı dene
    success = await play_music(message.chat.id, video_info)
    
    if success:
        # Şarkı bilgilerini gönder (FOTOĞRAFLI MESAJ)
        duration_text = saniyeyi_formatla(video_info["duration"])
        
        caption_text = (
            f"🎵 **Oynatılıyor**\n\n"
            f"📝 **Başlık:** `{video_info['title']}`\n"
            f"🕒 **Süre:** `{duration_text}`\n"
            f"👤 **İsteyen:** {message.from_user.mention}\n\n"
            f"🎧 **Asistan sesli sohbette.**"
        )
        
        await message.reply_photo(
            photo=video_info["thumbnail"],
            caption=caption_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏸ Durdur", callback_data="stop_cb"),
                 InlineKeyboardButton("⏹ Bitir", callback_data="end_cb")]
            ])
        )
        await m.delete() # "Aranıyor..." mesajını sil
    else:
        await m.edit("❌ **Hata:** Asistan sesli sohbete katılamadı. Sohbetin açık olduğundan emin olun.")

@app.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply_text("⏸ **Müzik durduruldu.**\nDevam etmek için `/resume` yazabilirsiniz.")
    except:
        await message.reply_text("❌ **Hata:** Şu an çalan bir müzik yok.")

@app.on_message(filters.command("resume") & filters.group)
async def resume(client, message):
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Müzik devam ettiriliyor.**")
    except:
        await message.reply_text("❌ **Hata:** Durdurulmuş bir müzik yok.")

@app.on_message(filters.command("end") & filters.group)
async def end(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        queue.clear()
        # İndirilen dosyaları temizle (Güvenlik için)
        for file in os.listdir("downloads"):
            os.remove(os.path.join("downloads", file))
        await message.reply_text("⏹ **Müzik sonlandırıldı ve kuyruk temizlendi.** Asistan ayrıldı.")
    except:
        await message.reply_text("❌ **Hata:** Asistan zaten sohbette değil.")

@app.on_message(filters.command("que") & filters.group)
async def show_queue(client, message):
    if not queue:
        return await message.reply_text("🗒 **Şarkı kuyruğu şu an boş.**")
    
    list_text = "🗒 **Şarkı Kuyruğu:**\n\n"
    for i, title in enumerate(queue, 1):
        list_text += f"{i}. `{title}`\n"
    await message.reply_text(list_text)

# --- BOTU BAŞLAT ---

if __name__ == "__main__":
    print("Bot ve Asistan başlatılıyor...")
    assistant.start() # Userbot giriş yapar
    call_py.start()   # Ses motoru başlar
    app.run()         # Ana bot çalışır
