import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

async def is_admin(client, chat_id, user_id):
    if user_id == config.SUDO_OWNER_ID or user_id in (config.SUDO_USERS or []):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and member.privileges.can_manage_video_chats
    except: return False

@Client.on_message(filters.command(["play", "p"]) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("❌ Lütfen şarkı adı yazın.")
    
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    msg = await message.reply("🔍 Aranıyor...")
    
    try:
        result = search_youtube(query)
        join_status = await assistant_join(client, chat_id)
        if join_status is not True: return await msg.edit(f"❌ Asistan hatası: {join_status}")

        status = await player.add_to_queue_or_play(chat_id, result, user_name)
        await msg.delete()

        if status == "PLAYING":
            await message.reply_photo(photo=result['thumbnail'], caption=player.format_playing_message(result, user_name), reply_markup=player.get_player_ui())
        elif status == "QUEUED":
            q_pos = len(player.music_queue[chat_id]) - 1
            await message.reply_photo(photo=result['thumbnail'], caption=f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n📌 {result['title']}")
        elif status == "FULL": await message.reply("❌ Kuyruk dolu!")
    except Exception as e: await msg.edit(f"❌ Hata: {str(e)}")

@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    next_song = await player.stream_end_handler(message.chat.id)
    if next_song and next_song != "EMPTY":
        await message.reply_photo(photo=next_song['info']['thumbnail'], caption=f"⏭ **Atlandı!**\n" + player.format_playing_message(next_song['info'], next_song['by']), reply_markup=player.get_player_ui())

@Client.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    player.clear_entire_queue(message.chat.id)
    try: await player.call.leave_call(message.chat.id)
    except: pass
    await message.reply("🛑 Durduruldu ve kuyruk temizlendi.")

@Client.on_message(filters.command(["que", "kuyruk"]) & filters.group)
async def queue_cmd(client, message: Message):
    chat_queue = player.music_queue.get(message.chat.id, [])
    if not chat_queue: return await message.reply("📂 Kuyruk boş.")
    
    text = "📜 **MÜZİK KUYRUĞU**\n\n"
    for i, song in enumerate(chat_queue):
        status = "🎧 Çalan" if i == 0 else f"{i}."
        text += f"**{status}** [{song['info']['title']}]({song['info']['webpage_url']})\n"

    img_path = os.path.join(os.getcwd(), "que.png")
    if os.path.exists(img_path): await message.reply_photo(photo=img_path, caption=text)
    else: await message.reply(text, disable_web_page_preview=True)

@Client.on_message(filters.command(["sil", "del"]) & filters.group)
async def del_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if len(message.command) == 1:
        player.clear_queue_except_current(message.chat.id)
        await message.reply("🧹 Bekleyen şarkılar silindi.")
    else:
        try:
            index = int(message.command[1])
            removed = player.remove_song_from_queue(message.chat.id, index)
            if removed: await message.reply(f"🗑 Silindi: {removed['info']['title']}")
        except: await message.reply("❌ Geçersiz sıra.")
