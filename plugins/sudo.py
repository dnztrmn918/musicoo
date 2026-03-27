from pyrogram import Client, filters
import config, player, asyncio
from database import get_served_chats, get_served_users

@Client.on_message(filters.command("reload") & filters.group)
async def reload(c, m):
    await c.get_chat_administrators(m.chat.id)
    await m.reply("✅ Önbellek yenilendi.")

@Client.on_message(filters.command("reloads"))
async def reloads(c, m):
    if m.from_user.id not in config.SUDO_USERS: return
    player.music_queue.clear()
    await m.reply("✅ Sistem ve tüm kuyruklar sıfırlandı.")

@Client.on_message(filters.command(["broadcast", "reklam"]))
async def broadcast(c, m):
    if m.from_user.id not in config.SUDO_USERS: return
    all_ids = list(set(await get_served_chats() + await get_served_users()))
    sent = 0
    for target in all_ids:
        try:
            if m.reply_to_message: await m.reply_to_message.copy(target)
            else: await c.send_message(target, m.text.split(None, 1)[1])
            sent += 1
            await asyncio.sleep(0.1)
        except: pass
    await m.reply(f"✅ Tamamlandı. Başarılı: {sent}")
