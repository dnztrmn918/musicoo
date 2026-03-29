import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

BOT_NAME = "Pi Müzik"
DEFAULT_LOGO = "plugins/logo.jpg"

async def is_admin(client, chat_id, user_id):
    from database import is_sudo
    if await is_sudo(user_id): return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and (member.privileges.can_manage_video_chats or member.status.value in ["creator", "administrator"])
    except: return False

@Client.on_message(filters.command(["play", "p", "oynat"]) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("❌ **Şarkı adı veya linki yazmalısın.**")
    
    msg = await message.reply(f"🔍 **{BOT_NAME}** arıyor ve indiriyor...")
    try:
        result = search_youtube(query)
        if not result: return await msg.edit("❌ Şarkı bulunamadı.")

        join_status = await assistant_join(client, message.chat.id)
        if join_status is not True: return await msg.edit(f"❌ Asistan hatası: {join_status}")

        status, extra = await player.add_to_queue_or_play(message.chat.id, result, message.from_user.first_name)
        try: await msg.delete()
        except: pass

        if status == "PLAYING":
            if message.chat.id in player.last_message_ids:
                try: await client.delete_messages(message.chat.id, player.last_message_ids[message.chat.id])
                except: pass
            
            sent_p = await message.reply_photo(
                photo=result.get('thumbnail') or DEFAULT_LOGO,
                caption=player.format_playing_message(result, message.from_user.first_name),
                reply_markup=player.get_player_ui()
            )
            player.last_message_ids[message.chat.id] = sent_p.id

        elif status == "QUEUED":
            q_pos = extra
            caption_text = f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n📌 **Parça:** `{result['title']}`\n👤 **İsteyen:** {message.from_user.first_name}"
            await message.reply_photo(photo=result.get('thumbnail') or DEFAULT_LOGO, caption=caption_text)
            
        elif status == "ERROR":
            await message.reply(f"❌ **Oynatma Hatası:** {extra}")

    except Exception as e:
        await message.reply(f"❌ **Hata:** {str(e)[:50]}")

@Client.on_message(filters.command(["stop", "dur", "pause", "durdur"]) & filters.group)
async def pause_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.pause_stream(message.chat.id):
        await message.reply("⏸ **Müzik duraklatıldı.**")

@Client.on_message(filters.command(["devam", "resume", "r"]) & filters.group)
async def resume_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.resume_stream(message.chat.id):
        await message.reply("▶️ **Müzik kaldığı yerden devam ediyor.**")

@Client.on_message(filters.command(["skip", "geç", "atla"]) & filters.group)
async def skip_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    await player.stream_end_handler(message.chat.id, action="skip")

@Client.on_message(filters.command(["end", "bitir", "son"]) & filters.group)
async def end_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    player.clear_entire_queue(message.chat.id)
    await player.stream_end_handler(message.chat.id, action="end")

@Client.on_message(filters.command(["sil", "temizle", "clear"]) & filters.group)
async def clean_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    player.clear_queue_except_current(message.chat.id)
    await message.reply("🗑️ **Kuyruk temizlendi (Çalan hariç).**")

@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def player_callbacks(client, query: CallbackQuery):
    c_id = query.message.chat.id
    if not await is_admin(client, c_id, query.from_user.id):
        return await query.answer("❌ Yetkin yok.", show_alert=True)

    try:
        if query.data == "pause":
            if await player.pause_stream(c_id): await query.answer("⏸ Durduruldu")
        elif query.data == "resume":
            if await player.resume_stream(c_id): await query.answer("▶️ Devam ediyor")
        elif query.data == "skip":
            await query.answer("⏭ Atlanıyor...")
            await player.stream_end_handler(c_id, action="skip")
        elif query.data == "end":
            await query.answer("⏹ Bitiriliyor...")
            player.clear_entire_queue(c_id)
            await player.stream_end_handler(c_id, action="end")
    except FloodWait as e:
        await asyncio.sleep(e.value)
