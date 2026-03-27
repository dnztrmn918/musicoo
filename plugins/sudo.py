from pyrogram import Client, filters
import config
import player
from database import get_served_chats, get_served_users
import asyncio

PREFIXES = ["/", "."]

# /reload: HERKESE AÇIK (Sadece o grubun önbelleğini / yönetici listesini yeniler)
@Client.on_message(filters.command(["reload", "yenile"], prefixes=PREFIXES) & filters.group)
async def reload_cmd(client, message):
    try:
        # Pyrogram'ın o grup için tuttuğu yönetici (admin) önbelleğini tazeler
        await client.get_chat_administrators(message.chat.id)
        await message.reply_text("✅ Grubun yönetici yetkileri ve yerel önbellek başarıyla güncellendi!")
    except Exception:
        await message.reply_text("❌ Önbellek yenilenirken bir hata oluştu.")

# /reloads: SADECE SUDO (Tüm sunucuyu, veritabanını ve bot kuyruklarını sıfırlar)
@Client.on_message(filters.command(["reloads", "sunucuyenile"], prefixes=PREFIXES))
async def reloads_cmd(client, message):
    if message.from_user.id not in config.SUDO_USERS:
        return # Sudo değilse hiçbir tepki vermez, gizliliği korur
    
    player.music_queue.clear()
    await message.reply_text("✅ **SİSTEM SIFIRLANDI!**\n\nSunucu veritabanı, bot genel önbelleği ve tüm gruplardaki aktif müzik kuyrukları başarıyla temizlendi.")

# /broadcast: SADECE SUDO (Genel Duyuru/Reklam Komutu)
@Client.on_message(filters.command(["broadcast", "reklam"], prefixes=PREFIXES))
async def broadcast_cmd(client, message):
    if message.from_user.id not in config.SUDO_USERS:
        return
        
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ Lütfen bir mesaja yanıt verin veya komuttan sonra bir duyuru metni yazın.")

    chats = await get_served_chats()
    users = await get_served_users()
    
    # Hedef kitlenin tekrarlanmasını engellemek için listeleri birleştir
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
            await asyncio.sleep(0.1) # Botun Telegram spama düşmemesi için mikro bekleme
        except:
            failed += 1
            
    await msg.edit_text(f"✅ **Yayın Tamamlandı!**\n\n📤 Başarılı: `{sent}`\n❌ Başarısız: `{failed}`")
