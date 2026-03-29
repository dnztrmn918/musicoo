import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

BOT_NAME = "Pi Müzik"
DEFAULT_LOGO = "plugins/logo.jpg"

# Yetki kontrolü
async def is_admin(client, chat_id, user_id):
    if user_id == config.SUDO_OWNER_ID or user_id in (config.SUDO_USERS or []):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and (member.privileges.can_manage_video_chats or member.status in ["creator", "administrator"])
    except: return False

# --- OYNATMA KOMUTU ---
@Client.on_message(filters.command(["play", "p", "oynat"]) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("❌ **Şarkı adı yazmalısın reis.**")
    
    msg = await message.reply(f"🔍 **{BOT_NAME}** arıyor...")
    try:
        result = search_youtube(query)
        if not result: return await msg.edit("❌ Şarkı bulunamadı.")

        join_status = await assistant_join(client, message.chat.id)
        if join_status is not True: return await msg.edit(f"❌ Asistan giremedi: {join_status}")

        status = await player.add_to_queue_or_play(message.chat.id, result, message.from_user.first_name)
        await msg.delete()

        if status == "PLAYING":
            sent_p = await message.reply_photo(
                photo=result.get('thumbnail') or DEFAULT_LOGO,
                caption=player.format_playing_message(result, message.from_user.first_name),
                reply_markup=player.get_player_ui()
            )
            player.last_message_ids[message.chat.id] = sent_p.id
        elif status == "QUEUED":
            await message.reply(f"⏳ **Kuyruğa Eklendi:** `{result['title']}`")
    except Exception as e:
        await message.reply(f"❌ **Hata:** {str(e)[:50]}")

# --- METİN KOMUTLARI (Yazarak Çalışanlar) ---
@Client.on_message(filters.command(["skip", "atla", "next", "n"]) & filters.group)
async def skip_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    await player.call.drop_call(message.chat.id)
    await message.reply("⏭ **Şarkı atlandı!**")

@Client.on_message(filters.command(["stop", "end", "bitir", "dur", "son"]) & filters.group)
async def stop_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    player.clear_entire_queue(message.chat.id)
    await player.call.leave_call(message.chat.id)
    await message.reply("🛑 **Müzik durduruldu, Pi Müzik çıktı.**")

@Client.on_message(filters.command(["resume", "devam", "r"]) & filters.group)
async def resume_text_cmd(client, message: Message):
    if await player.resume_stream(message.chat.id):
        await message.reply("▶️ **Müzik devam ediyor.**")

@Client.on_message(filters.command(["pause", "durdur", "beklet"]) & filters.group)
async def pause_text_cmd(client, message: Message):
    if await player.pause_stream(message.chat.id):
        await message.reply("⏸ **Müzik duraklatıldı.**")

@Client.on_message(filters.command(["sil", "temizle", "clear"]) & filters.group)
async def clean_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    player.clear_queue_except_current(message.chat.id)
    await message.reply("🗑️ **Kuyruk temizlendi (Çalan hariç).**")

# --- BUTON KOMUTLARI (İkonlara Basınca Çalışanlar) ---
@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def player_callbacks(client, query: CallbackQuery):
    c_id = query.message.chat.id
    if not await is_admin(client, c_id, query.from_user.id):
        return await query.answer("❌ Yetkin yok reis.", show_alert=True)

    if query.data == "pause":
        if await player.pause_stream(c_id): await query.answer("⏸ Durduruldu")
    elif query.data == "resume":
        if await player.resume_stream(c_id): await query.answer("▶️ Devam ediyor")
    elif query.data == "skip":
        await player.call.drop_call(c_id)
        await query.answer("⏭ Atlandı")
    elif query.data == "end":
        player.clear_entire_queue(c_id)
        await player.call.leave_call(c_id)
        await query.answer("🛑 Bitirildi")
        await query.message.delete()
