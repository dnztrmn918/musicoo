import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus

active_tagging = {}

G_MESSAGES = ["Günaydın güneş parçaları! ☀️", "Yeni gün, yeni umutlar! ☕", "Uyanın millet, sabah oldu! 🌅"]
I_MESSAGES = ["Yıldızlar kadar parlak rüyalar... ✨", "Huzurlu bir gece dilerim. 🌙", "İyi uykular, tatlı rüyalar. 😴"]
S_MESSAGES = ["Sohbetin tadı sizsiz çıkmıyor! 🔥", "Gelin iki lafın belini kıralım. 🗣️", "Sohbet odası aktif, hadi gelin! 💬"]
K_MESSAGES = ["Kurtlar sofrasına davetlisiniz! 🐺", "Pençeler hazır mı? Kurt oyunu başlıyor! ⚔️"]

@Client.on_message(filters.command(["tag", "utag", "gtag", "itag", "stag", "ktag"]) & filters.group)
async def unified_tagger(client, message):
    chat_id = message.chat.id
    if chat_id in active_tagging:
        return await message.reply("⚠️ Zaten aktif bir etiketleme var!")

    # 🔥 YETKİ KONTROLÜ DÜZELTİLDİ (Enum Kullanımı)
    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if user.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply("❌ Yetkiniz yok.")
    except Exception:
        return await message.reply("❌ Yetki kontrolü yapılamadı.")

    cmd = message.command[0].lower()
    active_tagging[chat_id] = 0 
    m = await message.reply(f"🚀 **{cmd.upper()}** işlemi başlatıldı!")

    try:
        async for member in client.get_chat_members(chat_id):
            if chat_id not in active_tagging: break
            if member.user.is_bot or member.user.is_deleted: continue
            
            if cmd in ["tag", "utag"]: tag_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Etiketleniyorsunuz..."
            elif cmd == "gtag": tag_msg = random.choice(G_MESSAGES)
            elif cmd == "itag": tag_msg = random.choice(I_MESSAGES)
            elif cmd == "stag": tag_msg = random.choice(S_MESSAGES)
            elif cmd == "ktag": tag_msg = random.choice(K_MESSAGES)

            try:
                await client.send_message(chat_id, f"{tag_msg}\n👤 {member.user.mention}")
                active_tagging[chat_id] += 1 
                await asyncio.sleep(2.5)
            except:
                await asyncio.sleep(5)
                continue
    finally:
        if chat_id in active_tagging:
            final_count = active_tagging.pop(chat_id)
            await m.reply(f"✅ İşlem bitti. Toplam etiketlenen: `{final_count}`")

@Client.on_message(filters.command(["cancel", "iptal", "tagdur"]) & filters.group)
async def cancel_tagging(client, message):
    chat_id = message.chat.id
    if chat_id in active_tagging:
        count = active_tagging.pop(chat_id) 
        await message.reply(f"⏹ **İşlem Durduruldu!**\n👤 **Durduran:** {message.from_user.mention}\n📊 **Etiketlenen:** `{count}`")
    else:
        await message.reply("❌ Şu an aktif bir işlem bulunmuyor.")
