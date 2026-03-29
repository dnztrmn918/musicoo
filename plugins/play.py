import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

# Bot ismi ve estetik ayarlar
BOT_NAME = "Pi Müzik"
DEFAULT_LOGO = "plugins/logo.jpg"

async def is_admin(client, chat_id, user_id):
    if user_id == config.SUDO_OWNER_ID or user_id in (config.SUDO_USERS or []):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and (member.privileges.can_manage_video_chats or member.status == "creator")
    except: return False

@Client.on_message(filters.command(["play", "p"]) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("❌ **Lütfen şarkı adı veya link girin.**")
    
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    msg = await message.reply(f"🔍 **{BOT_NAME}** üzerinden aranıyor...")
    
    try:
        result = search_youtube(query)
        join_status = await assistant_join(client, chat_id)
        if join_status is not True: 
            return await msg.edit(f"❌ **Asistan hatası:** {join_status}")

        status = await player.add_to_queue_or_play(chat_id, result, user_name)
        
        # Arama mesajını temizle
        try: await msg.delete()
        except: pass

        if status == "PLAYING":
            # Eski mesajı temizle
            if chat_id in player.last_message_ids:
                try: await client.delete_messages(chat_id, player.last_message_ids[chat_id])
                except: pass
            
            # --- RESİM KONTROL MANTIĞI ---
            try:
                # 1. Önce şarkının kendi thumbnail'ını dene
                sent_p = await message.reply_photo(
                    photo=result['thumbnail'], 
                    caption=player.format_playing_message(result, user_name), 
                    reply_markup=player.get_player_ui()
                )
            except Exception:
                # 2. Şarkı resmi bozuksa/yoksa varsayılan logo.jpg'yi gönder
                try:
                    sent_p = await message.reply_photo(
                        photo=DEFAULT_LOGO,
                        caption=player.format_playing_message(result, user_name), 
                        reply_markup=player.get_player_ui()
                    )
                except Exception:
                    # 3. Logo da yoksa sadece metin gönder
                    sent_p = await message.reply(
                        text=player.format_playing_message(result, user_name),
                        reply_markup=player.get_player_ui()
                    )
            player.last_message_ids[chat_id] = sent_p.id

        elif status == "QUEUED":
            q_pos = len(player.music_queue[chat_id]) - 1
            caption_text = f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n📌 **Parça:** {result['title']}\n👤 **İsteyen:** {user_name}"
            try:
                await message.reply_photo(photo=result['thumbnail'], caption=caption_text)
            except Exception:
                try:
                    await message.reply_photo(photo=DEFAULT_LOGO, caption=caption_text)
                except Exception:
                    await message.reply(caption_text)

    except Exception as e: 
        try: await msg.edit(f"❌ **Hata:** {str(e)[:100]}")
        except: await message.reply(f"❌ **Hata:** {str(e)[:100]}")

# --- CALLBACK VE YÖNETİM KOMUTLARI ---
@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def player_callbacks(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("❌ Bu işlemi sadece yöneticiler yapabilir.", show_alert=True)

    data = query.data
    if data == "pause":
        if await player.pause_stream(chat_id): await query.answer("⏸ Müzik duraklatıldı.")
    elif data == "resume":
        if await player.resume_stream(chat_id): await query.answer("▶️ Müzik devam ediyor.")
    elif data == "skip":
        await query.answer("⏭ Şarkı atlandı!")
        await client.send_message(chat_id, "⏭ **Şarkı atlandı!**")
        await player.stream_end_handler(chat_id)
    elif data == "end":
        player.clear_entire_queue(chat_id)
        try: await player.call.leave_call(chat_id)
        except: pass
        try: await query.message.delete()
        except: pass
        await client.send_message(chat_id, f"🛑 **{BOT_NAME} yayını sonlandırdı.**")

@Client.on_message(filters.command(["que", "kuyruk"]) & filters.group)
async def queue_cmd(client, message: Message):
    chat_queue = player.music_queue.get(message.chat.id, [])
    if not chat_queue: return await message.reply("📂 **Kuyruk şu an boş.**")
    
    text = f"🎵 **{BOT_NAME} - Canlı Müzik Kuyruğu** 🎵\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, song in enumerate(chat_queue):
        if i == 0:
            text += f"🎧 **Şu An Çalan:**\n └ 🎶 `{song['info']['title']}`\n\n"
            if len(chat_queue) > 1: text += "⏳ **Sıradakiler:**\n"
        else:
            text += f" `{i}.` 📌 {song['info']['title']}\n"
    text += "\n━━━━━━━━━━━━━━━━━━━━"
    
    # Öncelik que.png, yoksa logo.jpg
    que_photo = "que.png" if os.path.exists("que.png") else DEFAULT_LOGO if os.path.exists(DEFAULT_LOGO) else None

    try:
        if que_photo: await message.reply_photo(photo=que_photo, caption=text)
        else: await message.reply(text)
    except Exception: await message.reply(text)
