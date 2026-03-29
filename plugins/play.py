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
        if not result:
            return await msg.edit("❌ **Şarkı bulunamadı!**")

        join_status = await assistant_join(client, chat_id)
        if join_status is not True: 
            return await msg.edit(f"❌ **Asistan hatası:** {join_status}")

        status = await player.add_to_queue_or_play(chat_id, result, user_name)
        
        # Arama mesajını temizle
        try: await msg.delete()
        except: pass

        if status == "PLAYING":
            # Eski mesajı temizle (Varsa)
            if chat_id in player.last_message_ids:
                try: await client.delete_messages(chat_id, player.last_message_ids[chat_id])
                except: pass
            
            # --- RESİM KONTROL MANTIĞI ---
            try:
                sent_p = await message.reply_photo(
                    photo=result['thumbnail'], 
                    caption=player.format_playing_message(result, user_name), 
                    reply_markup=player.get_player_ui()
                )
            except Exception:
                try:
                    sent_p = await message.reply_photo(
                        photo=DEFAULT_LOGO,
                        caption=player.format_playing_message(result, user_name), 
                        reply_markup=player.get_player_ui()
                    )
                except Exception:
                    sent_p = await message.reply(
                        text=player.format_playing_message(result, user_name),
                        reply_markup=player.get_player_ui()
                    )
            player.last_message_ids[chat_id] = sent_p.id

        elif status == "QUEUED":
            q_pos = len(player.music_queue[chat_id]) - 1
            caption_text = f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n📌 **Parça:** `{result['title']}`\n👤 **İsteyen:** {user_name}"
            try:
                await message.reply_photo(photo=result['thumbnail'], caption=caption_text)
            except Exception:
                try: await message.reply_photo(photo=DEFAULT_LOGO, caption=caption_text)
                except Exception: await message.reply(caption_text)

    except Exception as e: 
        print(f"Play Hatası: {e}")
        try: await message.reply(f"❌ **Hata:** {str(e)[:100]}")
        except: pass

# --- CALLBACK VE YÖNETİM KOMUTLARI ---
@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def player_callbacks(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("❌ Bu işlemi sadece yöneticiler yapabilir.", show_alert=True)

    data = query.data
    
    if data == "pause":
        if await player.pause_stream(chat_id):
            await query.answer("⏸ Müzik duraklatıldı.")
        else:
            await query.answer("⚠️ Şu an duraklatılamıyor.", show_alert=True)

    elif data == "resume":
        if await player.resume_stream(chat_id):
            await query.answer("▶️ Müzik devam ediyor.")
        else:
            await query.answer("⚠️ Zaten devam ediyor.", show_alert=True)

    elif data == "skip":
        # Skip işleminde asistanı yeni şarkıya geçmesi için tetikliyoruz
        await query.answer("⏭ Şarkı atlanıyor...")
        # v2.x için en güvenli skip: Yayını düşürmek (handler otomatik sıradakine geçer)
        try:
            await player.call.drop_call(chat_id)
            await client.send_message(chat_id, "⏭ **Şarkı atlandı!**")
        except:
            # Drop call çalışmazsa manuel handler tetikle
            await player.stream_end_handler(chat_id)

    elif data == "end":
        await query.answer("⏹ Yayın sonlandırıldı.")
        player.clear_entire_queue(chat_id)
        try:
            await player.call.leave_call(chat_id)
            await query.message.delete()
        except: pass
        await client.send_message(chat_id, f"🛑 **{BOT_NAME} yayını sonlandırdı ve odadan ayrıldı.**")

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
    
    que_photo = "que.png" if os.path.exists("que.png") else DEFAULT_LOGO if os.path.exists(DEFAULT_LOGO) else None
    try:
        if que_photo: await message.reply_photo(photo=que_photo, caption=text)
        else: await message.reply(text)
    except Exception: await message.reply(text)
