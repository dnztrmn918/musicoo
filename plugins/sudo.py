from pyrogram import Client, filters
import config, player, asyncio
from database import get_served_chats, get_served_users

PREFIXES = ["/", "."]

@Client.on_message(filters.command("reloads", prefixes=PREFIXES))
async def reloads_cmd(c, m):
    if m.from_user.id not in config.SUDO_USERS: return
    player.music_queue.clear()
    await m.reply("✅ **SİSTEM SIFIRLANDI!**\nVeritabanı bağlantıları ve tüm aktif kuyruklar temizlendi.")

@Client.on_message(filters.command(["broadcast", "reklam"], prefixes=PREFIXES))
async def broadcast_cmd(c, m):
    if m.from_user.id not in config.SUDO_USERS: return
    
    if not m.reply_to_message and len(m.command) < 2:
        return await m.reply("⚠️ Lütfen bir duyuru metni yazın veya bir mesajı yanıtlayın.")

    all_chats = await get_served_chats()
    all_users = await get_served_users()
    targets = list(set(all_chats + all_users))
    
    status_msg = await m.reply(f"🚀 **Yayın Başlatıldı!**\nHedef Kitle: `{len(targets)}` birim.")
    
    sent = 0
    failed = 0
    for target_id in targets:
        try:
            if m.reply_to_message: await m.reply_to_message.copy(target_id)
            else: await c.send_message(target_id, m.text.split(None, 1)[1])
            sent += 1
            await asyncio.sleep(0.1) # Flood önleyici
        except: 
            failed += 1
    
    await status_msg.edit_text(f"✅ **Yayın Tamamlandı!**\n\n📤 Başarılı: `{sent}`\n❌ Başarısız: `{failed}`")
