import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

# YÖNETİCİ KONTROL SİSTEMİ
async def is_admin(client, chat_id, user_id):
    if user_id == config.SUDO_OWNER_ID or user_id in config.SUDO_USERS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and member.privileges.can_manage_video_chats
    except:
        return False

# ▶️ ŞARKI OYNATMA VE KUYRUK EKLENTİSİ
@Client.on_message(filters.command(["play", "p"]) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("❌ Lütfen bir şarkı adı yazın. (Örn: /play Sezen Aksu)")
        
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    
    msg = await message.reply("🔍 Şarkı aranıyor...")
    
    try:
        result = search_youtube(query)
        
        # Asistan Bağlantısı
        join_status = await assistant_join(client, chat_id)
        if join_status == "ADMIN_REQUIRED":
            return await msg.edit("❌ Asistanın gruba katılabilmesi için bana 'Davet Bağlantısı Oluşturma' yetkisi vermelisiniz!")
        elif join_status is not True:
            return await msg.edit(f"❌ Asistan katılamadı: {join_status}")
            
        status = await player.add_to_queue_or_play(chat_id, result, user_name)
        
        if status == "PLAYING":
            await msg.delete()
            await message.reply_photo(
                photo=result['thumbnail'],
                caption=player.format_playing_message(result, user_name),
                reply_markup=player.get_player_ui()
            )
        elif status == "QUEUED":
            await msg.delete()
            q_pos = len(player.music_queue[chat_id]) - 1
            await message.reply_photo(
                photo=result['thumbnail'],
                caption=f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n\n📌 **Şarkı:** [{result['title']}]({result['webpage_url']})\n👤 **İsteyen:** {user_name}"
            )
        elif status == "FULL":
            await msg.edit("❌ **Kuyruk dolu!** Maksimum 5 şarkı bekleyebilir.")
        else:
            await msg.edit(f"❌ Oynatma Hatası: {status}")
            
    except Exception as e:
        await msg.edit(f"❌ Hata: {str(e)}")

# ⏭ ŞARKI ATLAMA
@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Bu komutu sadece sesli sohbet yöneticileri kullanabilir.")
        
    next_song = await player.stream_end_handler(message.chat.id)
    if next_song and next_song != "EMPTY":
        await message.reply(f"⏭ **Şarkı atlandı!**\n🎶 **Şimdi çalıyor:** {next_song['info']['title']}")
    else:
        await message.reply("⏭ **Kuyruk bitti, asistan sesten ayrıldı.** 👋")

# 🛑 YAYINI DURDURMA VE ÇIKIŞ
@Client.on_message(filters.command(["stop", "end", "kapat"]) & filters.group)
async def stop_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Bu komutu sadece sesli sohbet yöneticileri kullanabilir.")
        
    player.clear_entire_queue(message.chat.id)
    try:
        # KRİTİK DEĞİŞİKLİK: leave_group_call artık leave_call oldu (V2 Uyumu)
        await player.call.leave_call(message.chat.id)
    except:
        pass
    await message.reply("🛑 **Müzik durduruldu ve kuyruk temizlendi. Asistan sesten ayrıldı.**")

# 📜 RESİMLİ VE HİZALI KUYRUK LİSTESİ
@Client.on_message(filters.command(["que", "list", "kuyruk"]) & filters.group)
async def queue_cmd(client, message: Message):
