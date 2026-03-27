from pyrogram import Client, filters
import config, player, asyncio
from database import get_served_chats, get_served_users

@Client.on_message(filters.command("reloads"))
async def reloads_cmd(c, m):
    if m.from_user.id not in config.SUDO_USERS: return
    player.music_queue.clear()
    await m.reply("⚙️ **SİSTEM SIFIRLANDI!** 🧹")

@Client.on_message(filters.command(["broadcast", "reklam"]))
async def broadcast_cmd(c, m):
    if m.from_user.id not in config.SUDO_USERS: return
    if not m.reply_to_message and len(m.command) < 2: return await m.reply("⚠️ Metin girin!")
    
    targets = list(set(await get_served_chats() + await get_served_users()))
    status = await m.reply(f"🚀 **Yayın Başlatıldı!** Target: `{len(targets)}`")
    
    sent = 0
    for t in targets:
        try:
            if m.reply_to_message: await m.reply_to_message.copy(t)
            else: await c.send_message(t, m.text.split(None, 1)[1])
            sent += 1
            await asyncio.sleep(0.1)
        except: pass
    await status.edit(f"✅ **Yayın Bitti!** Ulaşılan: `{sent}`")
