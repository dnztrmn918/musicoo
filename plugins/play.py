from pyrogram import Client, filters
from search import search_youtube
import player
import config
from assistant import assistant_join

@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_command(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2: return await message.reply("🔍 **Şarkı adı yazın.**")
    
    m = await message.reply("🕵️ **Asistan kontrol ediliyor...**")
    if not await assistant_join(client, chat_id):
        return await m.edit("❌ **Asistan katılamadı. Yetkilerimi kontrol edin.**")
    
    await m.edit("🔍 **Aranıyor...**")
    try:
        query = message.text.split(None, 1)[1]
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        await m.delete()
        
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"
        await message.reply_photo(photo=thumb, caption=player.format_playing_message(song_info, message.from_user.mention), reply_markup=player.get_player_ui())
    except Exception as e: await m.edit(f"❌ **Hata:** {e}")

@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message):
    res = await player.stream_end_handler(message.chat.id)
    if res == "EMPTY": await message.reply("⏹ **Kuyruk bitti.**")
    elif res: await message.reply(f"⏭ **Sıradaki:** `{res['info']['title']}`")

@Client.on_message(filters.command(["stop", "dur", "pause"]) & filters.group)
async def stop_cmd(client, message):
    try:
        await player.call.pause_stream(message.chat.id)
        await message.reply("⏸ **Durduruldu.**")
    except: pass

@Client.on_message(filters.command(["resume", "devam"]) & filters.group)
async def resume_cmd(client, message):
    try:
        await player.call.resume_stream(message.chat.id)
        await message.reply("▶️ **Devam ediyor.**")
    except: pass

@Client.on_message(filters.command(["end", "bitir"]) & filters.group)
async def end_cmd(client, message):
    player.music_queue.pop(message.chat.id, None)
    try:
        await player.call.leave_group_call(message.chat.id)
        await message.reply("⏹ **Yayın bitti.**")
    except: pass

@Client.on_message(filters.command(["que", "kuyruk", "list"]) & filters.group)
async def queue_cmd(client, message):
    if message.chat.id not in player.music_queue or not player.music_queue[message.chat.id]:
        return await message.reply("📭 **Kuyruk boş.**")
    text = "🎼 **Kuyruk Listesi**\n\n"
    for i, s in enumerate(player.music_queue[message.chat.id]):
        text += f"**{i}.** {s['info']['title']}\n"
    await message.reply(text)
