import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus

active_tagging = {}

G_MESSAGES = [
    "Günaydın güneş parçaları! ☀️", 
    "Yeni gün, yeni umutlar! ☕", 
    "Uyanın millet, sabah oldu! 🌅",
    "Gününüz aydın, neşeniz bol olsun! 🌼",
    "Kahveler hazır mı? Günaydınlar! ☕",
    "Erkenci kuşlar buraya! Herkese günaydın. 🕊️",
    "Harika bir gün geçirmeniz dileğiyle, günaydın! 🌞",
    "Sabahın ilk ışıklarıyla gruba energy saçmaya geldim, günaydın! ⚡"
]

I_MESSAGES = [
    "Yıldızlar kadar parlak rüyalar... ✨", 
    "Huzurlu bir gece dilerim. 🌙", 
    "İyi uykular, tatlı rüyalar. 😴",
    "Günün yorgunluğunu atma vakti, iyi geceler! 🌌",
    "Uyku perisi kapınızı çalsın, tatlı rüyalar! 🧚‍♀️",
    "Yarın daha güzel bir güne uyanmak dileğiyle, iyi uykular. 🌠",
    "Geceniz güzel, uykunuz derin olsun. 🌠",
    "Karanlığın huzuru üzerinize olsun, iyi geceler. 🦉"
]

S_MESSAGES = [
    "Elinizde tek bir gidiş bileti olsa şu an nereye uçardınız? ✈️",
    "Hayatınız bir film olsa arka planda şu an hangi şarkı çalardı? 🎵",
    "Şu ana kadar aldığınız en garip iltifat neydi? 😂",
    "Sınırsız bütçeniz olsa alacağınız ilk 'gereksiz' şey ne olurdu? 💰",
    "Zaman yolculuğu icat edilse, geçmişe mi giderdiniz geleceğe mi? ⏳",
    "Görünmezlik mi, yoksa uçabilmek mi? Tarafını seç, sohbete gel! 🦸‍♂️",
    "Bugün sizi en çok ne güldürdü? Gelin biraz da biz gülelim. 😆",
    "Asla yapmam deyip de yaptığınız en saçma şey neydi? 🙈",
    "Telefonunuzdaki en garip uygulama nedir? İtirafları alalım! 📱",
    "Bir günlüğüne başkasının yerine geçecek olsanız bu kim olurdu? 🎭",
    "Dünyadaki tüm insanlara aynı anda bir mesaj gönderebilseniz, ne yazardınız? 🌍",
    "Sadece 3 kelimeyle bugünkü modunuzu nasıl özetlersiniz? 📝",
    "Issız bir adaya düşseniz yanınıza alacağınız 3 dizi/film ne olurdu? 🎬",
    "Çocukken inandığınız en komik yalan neydi? 🤥",
    "Bir hayvanla 10 dakika konuşabilme şansınız olsa hangi hayvanı seçerdiniz? 🐈",
    "Uyandığınızda 10 yıl ileriye gitmiş olsanız Google'da aratacağınız ilk şey ne olurdu? 🔍",
    "Buzdolabınızı açtığınızda görmekten en çok mutlu olduğunuz şey ne? 🍕",
    "Şu an dünyadaki herhangi bir yemeği anında önünüze getirebilsek bu ne olurdu? 🍔",
    "Zombi kıyameti kopsa gruptan yanınıza alacağınız ilk 2 kişi kim olurdu? 🧟‍♂️",
    "Hayatınız boyunca tek bir renk giymek zorunda kalsanız hangi rengi seçerdiniz? 🎨"
]

K_MESSAGES = [
    "Kurtlar sofrasına davetlisiniz! 🐺", 
    "Pençeler hazır mı? Kurt oyunu başlıyor! ⚔️",
    "Köylüler uyusun, kurtlar uyansın! Oyun başlıyor. 🌕",
    "Kim masum, kim hain? Bulmak için toplanın! 🕵️‍♂️",
    "Dolunay yükseldi, av vakti geldi! 🩸",
    "Hayatta kalma mücadelesine hazır mısınız? 🏹",
    "Kasabada bu gece tehlike var, herkes meydana! 🏚️"
]

@Client.on_message(filters.command(["tag", "utag", "gtag", "itag", "stag", "ktag"]) & filters.group)
async def unified_tagger(client, message):
    chat_id = message.chat.id
    if chat_id in active_tagging:
        return await message.reply("⚠️ Zaten aktif bir etiketleme var!")

    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if user.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply("❌ Yetkiniz yok.")
    except Exception:
        return await message.reply("❌ Yetki kontrolü yapılamadı.")

    cmd = message.command[0].lower()
    active_tagging[chat_id] = 0 
    m = await message.reply(f"🚀 **{cmd.upper()}** işlemi (5'li gruplar halinde) başlatıldı!")

    try:
        members = []
        async for member in client.get_chat_members(chat_id):
            if chat_id not in active_tagging: break
            if member.user.is_bot or member.user.is_deleted: continue
            members.append(member.user.mention)

            # 5 kişiye ulaştığımızda veya döngü sonunda gönder
            if len(members) == 5:
                if cmd in ["tag", "utag"]: 
                    tag_msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Etiketleniyorsunuz..."
                elif cmd == "gtag": tag_msg = random.choice(G_MESSAGES)
                elif cmd == "itag": tag_msg = random.choice(I_MESSAGES)
                elif cmd == "stag": tag_msg = random.choice(S_MESSAGES)
                elif cmd == "ktag": tag_msg = random.choice(K_MESSAGES)

                mentions = " | ".join(members)
                try:
                    await client.send_message(chat_id, f"{tag_msg}\n\n{mentions}")
                    active_tagging[chat_id] += len(members)
                    members = [] # Listeyi boşalt
                    await asyncio.sleep(3) # Gruplar arası daha hızlı bekleme
                except:
                    await asyncio.sleep(5)
                    continue
        
        # Listede kalan son kişileri de etiketle (5'ten az kaldıysa)
        if members and chat_id in active_tagging:
            mentions = " | ".join(members)
            await client.send_message(chat_id, f"Sona kalanlar:\n\n{mentions}")
            active_tagging[chat_id] += len(members)

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
