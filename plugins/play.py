from pyrogram import Client, filters
from search import search_youtube
import player
from plugins.assistant import assistant_join
import os

@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_command(client, message):
    chat_id = message.chat.id
    is_audio_reply = bool(message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice))
        
    if not is_audio_reply and len(message.command) < 2: 
        return await message.reply("🔍 **Lütfen bir şarkı adı girin veya bir ses dosyasına yanıt verin.**")
    
    m = await message.reply("📡 **İşlem yapılıyor, asistan bağlanıyor...** ⏳")
    
    join_status = await assistant_join(client, chat_id)
    if join_status == "ADMIN_REQUIRED":
        return await m.edit("❌ **Beni yönetici yapmalı ve 'Davet Bağlantısı Oluşturma' yetkisi vermelisiniz.**")
    elif isinstance(join_status, str) and join_status.startswith("JOIN_ERROR:"):
        return await m.edit(f"❌ **Asistan gruba katılamadı!**\n\n🔎 **GERÇEK HATA:** `{join_status}`")

    try:
        if is_audio_reply:
            await m.edit("📥 **Ses dosyası hazırlanıyor...** ⏳")
            audio_msg = message.reply_to_message
            audio = audio_msg.audio or audio_msg.voice
            file_path = await audio_msg.download(file_name="downloads/")
            
            title = getattr(audio, "title", None) or getattr(audio, "file_name", None) or "Telegram Ses Dosyası"
            song_info = {
                'title': title,
                'thumbnail': "https://telegra.ph/file/69204068595f57731936c.jpg",
                'file_path': file_path,
                'webpage_url': "https://t.me/NowaDestek"
            }
        else:
            await m.edit("📡 **YouTube üzerinden aranıyor...** ⏳")
            query = message.text.split(None, 1)[1]
            song_info = search_youtube(query)
            
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        
        if str(res).startswith("ERROR_DETAIL:"):
            return await m.edit(f"❌ **Hata:** `{res.split('ERROR_DETAIL: ')[1]}`")
        elif res == "FULL":
            return await m.edit("⚠️ **Kuyruk dolu!**")
        
        # Mesaj ID hatasını önlemek için güvenli silme
        try: await m.delete()
        except: pass

        # WEBPAGE_MEDIA_EMPTY hatasına karşı Try-Except bloğu
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"
        caption = player.format_playing_message(song_info, message.from_user.mention)
        
        try:
            await message.reply_photo(
                photo=thumb, 
                caption=caption, 
                reply_markup=player.get_player_ui()
            )
        except Exception:
            # Fotoğraf patlarsa sadece metin göndererek botu kurtarıyoruz
            await message.reply_text(
                text=caption, 
                reply_markup=player.get_player_ui(),
                disable_web_page_preview=True
            )

    except Exception as e:
        try: await m.edit(f"❌ **İşlem Hatası:** `{e}`")
        except: await message.reply(f"❌ **İşlem Hatası:** `{e}`")

# --- Diğer komutlar (skip, end, pause vb.) dokunulmadan korundu ---
# (Kuyruk, atla, bitir, dur, devam komutları aynen devam eder)
