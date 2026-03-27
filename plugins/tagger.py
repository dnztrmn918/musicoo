import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus

active_tagging = {}

G_MESSAGES = ["Günaydın güneş parçaları! ☀️", "Yeni gün, yeni umutlar! ☕", "Uyanın millet, sabah oldu! 🌅", "Gününüz huzurla dolsun. 🍀", "Gülümseyin, bugün harika bir gün! ✨", "Sıcacık bir günaydın! 🔥", "Dünya dönerken siz hala uyuyor musunuz? 🌍", "Güzelliklerle dolu bir sabah dilerim. 🌸", "Kahveler hazırsa uyanalım! ☕✨", "Enerji dolu bir günaydın! ⚡", "Güne mutlu başlayın! 🎈", "Mutluluk kapınızdan eksik olmasın! 🗝️", "Hadi uyanın, macera başlıyor! 🚀", "En güzel sabahlar sizinle olsun! 💎", "Gününüz aydın, neşeniz bol olsun! 🌈"]
I_MESSAGES = ["Yıldızlar kadar parlak rüyalar... ✨", "Huzurlu bir gece dilerim. 🌙", "İyi uykular, tatlı rüyalar. 😴", "Yarın mucizelere uyanmanız dileğiyle. 🌌", "Gecenin sessizliği huzur getirsin. 🕯️", "Kalbinizdeki tüm dualar kabul olsun. 🙏", "Ay ışığı odanızı aydınlatsın. 🌒", "Dinlenme vakti geldi, iyi geceler! 🛌", "En güzel uykular sizin olsun. 💤", "Sabaha umutla uyanın. ✨🌙"]
S_MESSAGES = ["Sohbetin tadı sizsiz çıkmıyor! 🔥", "Gelin iki lafın belini kıralım. 🗣️", "Sohbet odası aktif, hadi gelin! 💬", "Sessizliği bozalım, neşelenelim! 🥁", "Burada harika bir muhabbet var! ✨", "Siz yoksanız bir kişi eksiğiz. 👥", "Günün kritiğini yapalım mı? 🤔", "Sohbete davetlisiniz! 🎉", "Hadi gel de bir sesini duyalım. 🔊", "Keyifli bir sohbet sizi bekler! ☕"]
K_MESSAGES = ["Kurtlar sofrasına davetlisiniz! 🐺", "Pençeler hazır mı? Kurt oyunu başlıyor! ⚔️", "Dolunay yükseldi, av vakti! 🌕", "Köyde kurt var, kim hayatta kalacak? 🏠", "Kurt adamlar aramızda! 👹", "Taktiksel bir mücadeleye hazır mısın? 🛡️", "Adalet yerini bulacak mı? Kurt oyunu! ⚖️", "Hadi gelin, avcıları belirleyelim! 🏹", "Gece çökünce sırlar ortaya çıkar... 🌑", "Kurt oyunu için üyeler bekleniyor! 🐾"]

@Client.on_message(filters.command(["tag", "utag", "gtag", "itag", "stag", "ktag"]) & filters.group)
async def unified_tagger(client, message):
    chat_id = message.chat.id
    if chat_id in active_tagging:
        return await message.reply("⚠️ Zaten aktif bir etiketleme var!")

    user = await client.get_chat_member(chat_id, message.from_user.id)
    if user.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await message.reply("❌ Yetkiniz yok.")

    cmd = message.command[0].lower()
    tag_msg = ""
    if cmd in ["tag", "utag"]: tag_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Etiketleniyorsunuz..."
    elif cmd == "gtag": tag_msg = random.choice(G_MESSAGES)
    elif cmd == "itag": tag_msg = random.choice(I_MESSAGES)
    elif cmd == "stag": tag_msg = random.choice(S_MESSAGES)
    elif cmd == "ktag": tag_msg = random.choice(K_MESSAGES)

    active_tagging[chat_id] = True
    count = 0
    await message.reply(f"🚀 **{cmd.upper()}** işlemi başlatıldı!")

    try:
        async for member in client.get_chat_members(chat_id):
            if chat_id not in active_tagging: break
            if member.user.is_bot or member.user.is_deleted: continue
            
            await client.send_message(chat_id, f"{tag_msg}\n👤 {member.user.mention}")
            count += 1
            await asyncio.sleep(3) # FloodWait Koruması
    finally:
        if chat_id in active_tagging:
            active_tagging.pop(chat_id)
            await client.send_message(chat_id, f"✅ İşlem bitti. Etiketlenen: `{count}`")

@Client.on_message(filters.command(["cancel", "iptal", "tagdur"]) & filters.group)
async def cancel_tagging(client, message):
    if message.chat.id in active_tagging:
        active_tagging.pop(message.chat.id)
        await message.reply(f"⏹ İşlem {message.from_user.mention} tarafından durduruldu.")
