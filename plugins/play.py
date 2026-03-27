from pyrogram import Client, filters
from search import search_youtube
import player
from plugins.assistant import assistant_join

# ────────────────────────────────────────────────
# OYNATMA KOMUTU (/play)
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_command(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2: 
        return await message.reply("🔍 **Lütfen bir şarkı adı veya link girin.**")
    
    m = await message.reply("📡 **Asistan bağlanıyor...**")
    
    join_status = await assistant_join(client, chat_id)
    if join_status == "ADMIN_REQUIRED":
        return await m.edit("❌ **Beni yönetici yapmalı ve 'Davet Bağlantısı Oluşturma' yetkisi vermelisiniz.**")
    elif not join_status:
        return await m.edit("❌ **Asistan şu an sese bağlanamıyor.**")

    try:
        query = message.text.split(None, 1)[1]
        song_info = search_youtube(query)
        
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        
        if res == "ERROR":
            return await m.edit("❌ **Asistan sese katılamadı!**\n\nGrupta sesli sohbetin **başlatıldığından** emin olun.")
        elif res == "FULL":
            return await m.edit("⚠️ **Kuyruk dolu!** (Maksimum 5 şarkı eklenebilir. Mevcutları silmek için `/sil` kullanın.)")
        
        await m.delete()
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"
        await message.reply_photo(
            photo=thumb, 
            caption=player.format_playing_message(song_info, message.from_user.mention), 
            reply_markup=player.get_player_ui()
        )
    except Exception as e:
        await m.edit(f"❌ **Arama Hatası:** `{e}`")

# ────────────────────────────────────────────────
# ATLA VE BİTİR KOMUTLARI (/skip, /end)
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["skip", "atla", "end", "bitir"]) & filters.group)
async def skip_end_cmd(client, message):
    chat_id = message.chat.id
    res = await player.stream_end_handler(chat_id)
    
    if res == "EMPTY":
        await message.reply("⏹ **Kuyruk bitti, asistan sesli sohbetten ayrıldı.** 👋")
    elif res:
        await message.reply(f"⏭ **Sıradaki parçaya geçildi:** `{res['info']['title']}`")
    else:
        await message.reply("📭 **Şu anda çalan veya atlanacak bir parça yok.**")

# ────────────────────────────────────────────────
# DURDUR VE DEVAM ET KOMUTLARI (/stop, /resume)
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["stop", "dur", "pause"]) & filters.group)
async def pause_cmd(client, message):
    chat_id = message.chat.id
    try:
        await player.call.pause_stream(chat_id)
        await message.reply("⏸ **Yayın duraklatıldı.** (Devam etmek için `/devam`)")
    except Exception:
        pass

@Client.on_message(filters.command(["resume", "devam"]) & filters.group)
async def resume_cmd(client, message):
    chat_id = message.chat.id
    try:
        await player.call.resume_stream(chat_id)
        await message.reply("▶️ **Yayın devam ediyor.**")
    except Exception:
        pass

# ────────────────────────────────────────────────
# KUYRUK LİSTELEME KOMUTU (/que)
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["que", "kuyruk", "list"]) & filters.group)
async def que_cmd(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue or not player.music_queue[chat_id]:
        return await message.reply("📭 **Kuyruk boş.**")
    
    text = "🎼 **Kuyruk Listesi**\n\n"
    for i, song in enumerate(player.music_queue[chat_id]):
        if i == 0:
            text += f"▶️ **Şu An Çalan:** `{song['info']['title']}`\n"
        else:
            text += f"**{i}.** `{song['info']['title']}`\n"
    await message.reply(text)

# ────────────────────────────────────────────────
# SİL KOMUTU (/sil)
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["sil", "temizle"]) & filters.group)
async def sil_cmd(client, message):
    chat_id = message.chat.id
    
    if chat_id not in player.music_queue or len(player.music_queue[chat_id]) <= 1:
        return await message.reply("📭 **Silinecek bir kuyruk yok.**")
    
    if len(message.command) == 1:
        player.music_queue[chat_id] = [player.music_queue[chat_id][0]]
        return await message.reply("🗑 **Kuyruk tamamen temizlendi!** (Şu an çalan parça devam ediyor)")
    
    try:
        index = int(message.command[1])
        max_index = len(player.music_queue[chat_id]) - 1
        
        if index < 1 or index > max_index:
            return await message.reply(f"⚠️ **Geçersiz sıra numarası!** (1 ile {max_index} arasında bir sayı girin)")
        
        removed = player.music_queue[chat_id].pop(index)
        await message.reply(f"🗑 **Sıradan çıkarıldı:** `{removed['info']['title']}`")
    except ValueError:
        await message.reply("⚠️ **Lütfen geçerli bir sayı girin.** (Örnek: `/sil 1`)")
