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
    if not query: return await message.reply("❌ **Şarkı adı yazmalısın.**")
    
    msg = await message.reply(f"🔍 **{BOT_NAME}** arıyor...")
    try:
        result = search_youtube(query)
        if not result: return await msg.edit("❌ Şarkı bulunamadı.")

        join_status = await assistant_join(client, message.chat.id)
        if join_status is not True: return await msg.edit(f"❌ Asistan hatası: {join_status}")

        status = await player.add_to_queue_or_play(message.chat.id, result, message.from_user.first_name)
        try: await msg.delete()
        except: pass

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

# --- DURDURMA KOMUTLARI (PAUSE YAPANLAR) ---
@Client.on_message(filters.command(["stop", "dur", "pause", "durdur", "beklet"]) & filters.group)
async def pause_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.pause_stream(message.chat.id):
        await message.reply("⏸ **Müzik duraklatıldı.**")

# --- DEVAM ET KOMUTLARI (RESUME YAPANLAR) ---
@Client.on_message(filters.command(["resume", "devam", "r"]) & filters.group)
async def resume_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.resume_stream(message.chat.id):
        await message.reply("▶️ **Müzik devam ediyor.**")

# --- ATLA VE BİTİR KOMUTLARI (SKIP/END YAPANLAR) ---
@Client.on_message(filters.command(["skip", "atla", "next", "n", "end", "bitir", "son"]) & filters.group)
async def skip_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    # Drop call, sıradaki şarkı varsa ona geçer, yoksa player.py içindeki bitiş mesajını atıp çıkar.
    await player.call.drop_call(message.chat.id)
    if message.command[0] in ["skip", "atla", "next", "n"]:
        await message.reply("⏭ **Şarkı atlandı.**")

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

    if query.data == "pause":
        if await player.pause_stream(c_id): await query.answer("⏸ Durduruldu")
    elif query.data == "resume":
        if await player.resume_stream(c_id): await query.answer("▶️ Devam ediyor")
    elif query.data == "skip" or query.data == "end":
        await player.call.drop_call(c_id)
        await query.answer("⏭ İşlem uygulandı")
