from pyrogram import Client, filters
import config
import player
from database import get_served_chats, get_served_users
import asyncio

PREFIXES = ["/", "."]

@Client.on_message(filters.command(["reload", "yenile"], prefixes=PREFIXES))
async def reload_cmd(client, message):
    if message.from_user.id not in config.SUDO_USERS:
        return
    
    player.music_queue.clear()
    await message.reply_text("✅ Botun önbelleği ve müzik kuyrukları tamamen temizlendi!")

@Client.on_message(filters.command(["broadcast", "reklam"], prefixes=PREFIXES))
async def broadcast_cmd(client, message):
    if message.from_user.id not in config.SUDO_USERS:
        return
        
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ Lütfen bir mesaja yanıt verin veya komuttan sonra bir mesaj yazın.")

    chats = await get_served_chats()
    users = await get_served_users()
    
    all_ids = list(set([chat['chat_id'] for chat in chats] + [user['user_id'] for user in users]))
    
    sent = 0
    failed = 0
    msg = await message.reply_text(f"⏳ Yayın başlatılıyor... Toplam hedef: {len(all_ids)}")
    
    for target in all_ids:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(target)
            else:
                await client.send_message(target, message.text.split(None, 1)[1])
            sent += 1
            await asyncio.sleep(0.1) # Botun Telegram tarafından engellenmesini (Flood) önler
        except:
            failed += 1
            
    await msg.edit_text(f"✅ Yayın Tamamlandı!\n\n📤 Başarılı: {sent}\n❌ Başarısız: {failed}")
