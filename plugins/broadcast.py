import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database import is_sudo, get_served_chats, get_served_users
import config

@Client.on_message(filters.command(["broadcast", "duyuru"]) & filters.private)
async def broadcast_cmd(client: Client, message: Message):
    if not await is_sudo(message.from_user.id):
        return await message.reply("⛔ **Bu komut sadece Sudo kullanıcıları içindir.**")

    # Duyurulacak mesajı belirle (Ya yanına yazılan metin ya da yanıtlanan mesaj)
    if message.reply_to_message:
        query = message.reply_to_message
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    else:
        return await message.reply("❌ **Duyuru yapılacak bir metin yazın veya bir mesaja yanıt verin.**\nÖrnek: `/duyuru Merhaba!`")

    sent_msg = await message.reply("📢 **Duyuru başlatılıyor...**")
    
    # Tüm chat ve kullanıcı ID'lerini veritabanından çekip birleştiriyoruz
    try:
        chats = await get_served_chats()
        users = await get_served_users()
        all_chats = chats + users
    except Exception as e:
        return await sent_msg.edit(f"❌ **Veritabanından chat listesi alınamadı.** Hata: {e}")

    done = 0
    failed = 0
    
    for chat_id in all_chats:
        try:
            if isinstance(query, Message):
                await query.copy(chat_id)
            else:
                await client.send_message(chat_id, query)
            done += 1
            await asyncio.sleep(0.3) # FloodWait yememek için kısa bekleme
        except Exception:
            failed += 1
            continue

    await sent_msg.edit(
        f"✅ **Duyuru Tamamlandı!**\n\n"
        f"👤 **Başarılı:** `{done}`\n"
        f"❌ **Hatalı:** `{failed}`"
    )
