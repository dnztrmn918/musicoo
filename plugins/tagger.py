import asyncio
import random
from pyrogram import Client, filters

# Sözlük artık {chat_id: etiket_sayisi} şeklinde veri tutacak
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
    if user.status not in ["creator", "administrator"]:
        return await message.reply("❌ Yetkiniz yok.")

    cmd = message.command[0].lower()
    active_tagging[chat_id] = 0 # Sayacı 0'dan başlatıyoruz
    await message.reply(f"🚀 **{cmd.upper()}** işlemi başlatıldı!")

    try:
        async for member in client.get_chat_members(chat_id):
            if chat_id not in active_tagging: break
            if member.user.is_bot or member.user.is_deleted: continue
            
            # Rastgele mesaj seçimi
            if cmd in ["tag", "utag"]: 
                tag_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Etiketleniyorsunuz..."
            elif cmd == "gtag": tag_msg = random.choice(G_MESSAGES)
            elif cmd == "itag": tag_msg = random.choice(I_MESSAGES)
            elif cmd == "stag": tag_msg = random.choice(S_MESSAGES)
            elif cmd == "ktag": tag_msg = random.choice(K_MESSAGES)

            try:
                await client.send_message(chat_id, f"{tag_msg}\n👤 {member.user.mention}")
                active_tagging[chat_id] += 1 # Global sayacı artır
                await asyncio.sleep(2.5)
            except Exception:
                await asyncio.sleep(5)
                continue
                
    finally:
        # Eğer işlem /cancel ile bitmediyse normal bitiş mesajı
        if chat_id in active_tagging:
            final_count = active_tagging.pop(chat_id)
            await client.send_message(chat_id, f"✅ İşlem bitti. Toplam etiketlenen: `{final_count}`")

@Client.on_message(filters.command(["cancel", "iptal", "tagdur"]) & filters.group)
async def cancel_tagging(client, message):
    chat_id = message.chat.id
    if chat_id in active_tagging:
        count = active_tagging.pop(chat_id) # Sayıyı al ve listeden sil
        await message.reply(
            f"⏹ **İşlem Durduruldu!**\n"
            f"👤 **Durduran:** {message.from_user.mention}\n"
            f"📊 **Etiketlenen Kişi Sayısı:** `{count}`"
        )
    else:
        await message.reply("❌ Şu an aktif bir işlem bulunmuyor.")
