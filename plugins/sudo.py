import time
import asyncio
from pyrogram import Client, filters
import config
from database import get_served_chats, get_served_users

@Client.on_message(filters.command("bilgi") & filters.user(config.SUDO_USERS))
async def info_to_channel(client, message):
    start_t = time.time()
    m = await message.reply_text("📊 **Veriler toplanıyor...**")
    
    try:
        all_chats = await get_served_chats()
        all_users = await get_served_users()
        ping = f"{round((time.time() - start_t) * 1000)} ms"
        
        stats_text = (
            "📢 **MÜZİK BOTU GÜNCEL RAPORU**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏠 **Toplam Grup:** `{len(all_chats)}` grup\n"
            f"👥 **Toplam Kullanıcı:** `{len(all_users)}` kişi\n"
            f"⚡️ **Ping:** `{ping}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 **Tarih:** {time.strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        await client.send_message(config.STATS_CHANNEL_ID, stats_text)
        await m.edit("✅ **İstatistikler kanala gönderildi!**")
    except Exception as e:
        await m.edit(f"❌ Hata oluştu: {e}")

@Client.on_message(filters.command("duyuru") & filters.user(config.SUDO_USERS))
async def broadcast(client, message):
    # Hatalı olan 'if not message' kısmı burada düzeltildi:
    if not message.reply_to_message:
        return await message.reply("📢 Duyuru yapmak için bir mesaja yanıt verin!")
    
    chats = await get_served_chats()
    sent = 0
    m = await message.reply_text(f"🚀 Duyuru `{len(chats)}` gruba gönderiliyor...")
    
    for chat_id in chats:
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
            await asyncio.sleep(0.3)
        except:
            pass
            
    await m.edit(f"✅ **Duyuru tamamlandı!**\n📦 **Başarılı:** `{sent}`\n❌ **Hatalı:** `{len(chats) - sent}`")
