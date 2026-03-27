from pyrogram import Client, filters, enums
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
import config, asyncio
from database import add_served_chat

playing_messages = {}

async def has_voice_perms(client, chat_id, user_id):
    if user_id in config.SUDO_USERS: return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except: return False

@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_command(client, message):
    await add_served_chat(message.chat.id)
    chat_id = message.chat.id
    
    # Asistan Kontrolü
    try:
        await client.get_chat_member(chat_id, "PiMusicAssistan") 
    except:
        m_invite = await message.reply_text("🕵️ **Asistan aranıyor...**")
        try:
            from main import userbot
            link = await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(link)
            await m_invite.edit("✅ **Asistan katıldı!**")
        except:
            return await m_invite.edit("❌ **Asistan gelmedi.**")

    if len(message.command) < 2: return await message.reply("🔍 Şarkı adı girin.")
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 **Aranıyor...**")
    
    try:
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        await m.delete()
        
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"
        msg = await message.reply_photo(photo=thumb, caption=player.format_playing_message(song_info, message.from_user.mention), reply_markup=player.get_player_ui())
        playing_messages[chat_id] = msg
    except Exception as e: await m.edit(f"❌ Hata: {e}")

@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id): return
    res = await player.stream_end_handler(message.chat.id)
    if res == "EMPTY": await message.reply("⏹ Kuyruk bitti.")
    elif res: await message.reply(f"⏭ Sıradaki: {res['info']['title']}")

@Client.on_callback_query()
async def callbacks(client, query):
    chat_id = query.message.chat.id
    if query.data == "close_stats": return await query.message.delete()
    if not await has_voice_perms(client, chat_id, query.from_user.id): return await query.answer("Yetki yok!", show_alert=True)
    
    if query.data == "end":
        player.music_queue.pop(chat_id, None)
        await player.call.leave_group_call(chat_id)
        await query.message.delete()
    elif query.data == "skip":
        res = await player.stream_end_handler(chat_id)
        await query.message.delete()
        if res and res != "EMPTY":
            await client.send_photo(chat_id, photo=res['info'].get('thumbnail'), caption=player.format_playing_message(res['info'], res['by']), reply_markup=player.get_player_ui())
    elif query.data == "pause":
        await player.call.pause_stream(chat_id)
        await query.answer("⏸ Durduruldu.")
    elif query.data == "resume":
        await player.call.resume_stream(chat_id)
        await query.answer("▶️ Devam ediyor.")
