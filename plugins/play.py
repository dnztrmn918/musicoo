from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
import config, asyncio

# Yetki Kontrol Fonksiyonu
async def has_voice_perms(client, chat_id, user_id):
    if user_id in config.SUDO_USERS: return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except: return False

@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_cmd(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2: 
        return await message.reply("🔍 **Lütfen bir şarkı adı veya bağlantı girin.**")
    
    m = await message.reply("🔍 **Aranıyor...** ⏳")
    try:
        query = message.text.split(None, 1)[1]
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        await m.delete()
        
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"
        await message.reply_photo(
            photo=thumb, 
            caption=player.format_playing_message(song_info, message.from_user.mention), 
            reply_markup=player.get_player_ui()
        )
    except Exception as e:
        await m.edit(f"❌ **Hata:** {e}")

@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id): return
    res = await player.stream_end_handler(message.chat.id)
    if res == "EMPTY": await message.reply("⏹ **Kuyruk bitti, yayın durduruldu.**")
    elif res: await message.reply(f"⏭ **Sıradaki parça:**\n`{res['info']['title']}`")

@Client.on_message(filters.command(["stop", "dur", "pause"]) & filters.group)
async def stop_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id): return
    try:
        await player.call.pause_stream(message.chat.id)
        await message.reply("⏸ **Müzik duraklatıldı.**")
    except: pass

@Client.on_message(filters.command(["resume", "devam"]) & filters.group)
async def resume_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id): return
    try:
        await player.call.resume_stream(message.chat.id)
        await message.reply("▶️ **Müzik devam ediyor.**")
    except: pass

@Client.on_message(filters.command(["end", "bitir", "stopvc"]) & filters.group)
async def end_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id): return
    player.music_queue.pop(message.chat.id, None)
    try:
        await player.call.leave_group_call(message.chat.id)
        await message.reply("⏹ **Yayın sonlandırıldı ve kuyruk temizlendi.** 🧹")
    except: pass

@Client.on_message(filters.command(["que", "kuyruk", "list"]) & filters.group)
async def queue_cmd(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue or not player.music_queue[chat_id]:
        return await message.reply("📭 **Kuyruk şu an boş.**")
    
    text = "🎼 **Güncel Kuyruk Listesi**\n\n"
    for i, s in enumerate(player.music_queue[chat_id]):
        prefix = "▶️ **Şu an:** " if i == 0 else f"**{i}.** "
        text += f"{prefix}{s['info']['title']}\n"
    await message.reply(text)
