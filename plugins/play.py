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
    
    # 1. Kullanıcı bir ses dosyasına mı yanıt veriyor?
    is_audio_reply = False
    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
        is_audio_reply = True
        
    # 2. Hem yanıt yok hem de şarkı adı yoksa uyarı ver
    if not is_audio_reply and len(message.command) < 2: 
        return await message.reply("🔍 **Lütfen bir şarkı adı girin veya bir ses dosyasına yanıt verin.**")
    
    m = await message.reply("📡 **İşlem yapılıyor, asistan bağlanıyor...** ⏳")
    
    join_status = await assistant_join(client, chat_id)
    if join_status == "ADMIN_REQUIRED":
        return await m.edit("❌ **Beni yönetici yapmalı ve 'Davet Bağlantısı Oluşturma' yetkisi vermelisiniz.**")
    elif isinstance(join_status, str) and join_status.startswith("JOIN_ERROR:"):
        return await m.edit(f"❌ **Asistan gruba katılamadı!**\n\n🔎 **GERÇEK HATA:** `{join_status}`")
    elif not join_status:
        return await m.edit("❌ **Asistan şu an sese bağlanamıyor.**")

    try:
        # EĞER TELEGRAM SES DOSYASIYSA:
        if is_audio_reply:
            await m.edit("📥 **Telegram ses dosyası indiriliyor...** ⏳")
            audio_msg = message.reply_to_message
            audio = audio_msg.audio or audio_msg.voice
            
            # Telegram'dan sunucuya indir
            file_path = await audio_msg.download(file_name="downloads/")
            
            # Ses dosyasının bilgilerini ayarla
            title = getattr(audio, "title", None) or getattr(audio, "file_name", None) or "Telegram Ses Dosyası"
            duration = getattr(audio, "duration", 0)
            mins, secs = divmod(duration, 60)
            duration_str = f"{mins}:{secs:02d}" if duration else "Bilinmiyor"
            
            song_info = {
                'title': title,
                'duration': duration_str,
                'thumbnail': "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': file_path,
                'webpage_url': "https://t.me/NowaDestek"
            }
            
        # EĞER METİN YAZILDIYSA (Arama):
        else:
            await m.edit("📡 **Şarkı aranıyor ve indiriliyor...** ⏳")
            query = message.text.split(None, 1)[1]
            song_info = search_youtube(query)
            
        # Oynatıcıya gönder (İki yöntem de file_path döndürdüğü için sorunsuz çalışır)
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        
        if str(res).startswith("ERROR_DETAIL:"):
            hata_mesaji = res.split("ERROR_DETAIL: ")[1]
            return await m.edit(f"❌ **Asistan sese katılamadı!**\n\n🔎 **GERÇEK HATA:** `{hata_mesaji}`")
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
        await m.edit(f"❌ **İşlem Hatası:** `{e}`")

# ────────────────────────────────────────────────
# ATLA VE BİTİR KOMUTLARI (/skip, /end)
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["skip", "atla", "end", "bitir"]) & filters.group)
async def skip_end_cmd(client, message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()
    
    if cmd in ["end", "bitir"]:
        player.clear_entire_queue(chat_id)
        try: await player.call.leave_group_call(chat_id)
        except: pass
        return await message.reply("⏹ **Yayın sonlandırıldı, kuyruk ve dosyalar temizlendi.** 👋")

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
# KUYRUK VE SİLME KOMUTLARI (/que, /sil)
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

@Client.on_message(filters.command(["sil", "temizle"]) & filters.group)
async def sil_cmd(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue or len(player.music_queue[chat_id]) <= 1:
        return await message.reply("📭 **Silinecek bir kuyruk yok.**")
    if len(message.command) == 1:
        player.clear_queue_except_current(chat_id)
        return await message.reply("🗑 **Kuyruk tamamen temizlendi!** (Şu an çalan parça devam ediyor)")
    try:
        index = int(message.command[1])
        max_index = len(player.music_queue[chat_id]) - 1
        if index < 1 or index > max_index:
            return await message.reply(f"⚠️ **Geçersiz sıra numarası!** (1 ile {max_index} arasında bir sayı girin)")
        removed = player.remove_song_from_queue(chat_id, index)
        if removed:
            await message.reply(f"🗑 **Sıradan çıkarıldı:** `{removed['info']['title']}`")
    except ValueError:
        await message.reply("⚠️ **Lütfen geçerli bir sayı girin.** (Örnek: `/sil 1`)")

# ────────────────────────────────────────────────
# YENİ: MÜZİK BUTONLARI KONTROLÜ
# ────────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def music_callbacks(client, query):
    chat_id = query.message.chat.id
    data = query.data

    if data == "pause":
        try:
            await player.call.pause_stream(chat_id)
            await query.answer("⏸ Yayın duraklatıldı.")
        except:
            await query.answer("❌ İşlem başarısız.", show_alert=True)

    elif data == "resume":
        try:
            await player.call.resume_stream(chat_id)
            await query.answer("▶️ Yayın devam ediyor.")
        except:
            await query.answer("❌ İşlem başarısız.", show_alert=True)

    elif data == "skip":
        await query.answer("⏭ Sıradaki şarkıya geçiliyor...")
        res = await player.stream_end_handler(chat_id)
        if res == "EMPTY":
            await client.send_message(chat_id, "⏹ **Kuyruk bitti, asistan ayrıldı.** 👋")
            await query.message.delete()
        elif res:
            await client.send_message(chat_id, f"⏭ **Sıradaki:** `{res['info']['title']}`")
            await query.message.delete()

    elif data == "end":
        player.clear_entire_queue(chat_id)
        try: await player.call.leave_group_call(chat_id)
        except: pass
        await query.answer("⏹ Yayın bitirildi.")
        await query.message.delete()
        await client.send_message(chat_id, "⏹ **Yayın sonlandırıldı ve asistan odadan ayrıldı.** 👋")
