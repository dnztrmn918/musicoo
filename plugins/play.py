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
    
    # Asistan Davet Sistemi 
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
            return await m_invite.edit("❌ **Asistan gelmedi, manuel ekleyin.**")

    if len(message.command) < 2: return await message.reply("🔍 Şarkı adı girin.")
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 **Aranıyor...**")
    
    try:
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        
        if chat_id in playing_messages:
            try: await playing_messages[chat_id].delete()
            except: pass

        await m.delete()
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"

        if res == "ERROR":
            await message.reply("❌ **Asistan sesli sohbete giremedi.**")
        elif res == "FULL":
            await message.reply("⚠️ **Kuyruk dolu (Maks 5).**")
        elif res == "PLAYING":
            msg = await message.reply_photo(photo=thumb, caption=player.format_playing_message(song_info, message.from_user.mention), reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
        else:
            msg = await message.reply_photo(photo=thumb, caption=f"✅ **{song_info['title']}** kuyruğa eklendi!", reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
                
    except Exception as e: await m.edit(f"❌ Hata: {e}")

@Client.on_callback_query()
async def callbacks(client, query):
    chat_id = query.message.chat.id
    if query.data == "close_stats":
        return await query.message.delete()
        
    if not await has_voice_perms(client, chat_id, query.from_user.id):
        return await query.answer("Yetkiniz yok!", show_alert=True)
    
    if query.data == "end":
        player.music_queue.pop(chat_id, None) # Kuyruğu temizle 
        try: await player.call.leave_group_call(chat_id)
        except: pass
        await query.message.delete()
        await client.send_message(chat_id, "⏹ **Yayın sonlandırıldı ve kuyruk temizlendi.**")
    elif query.data == "skip":
        res = await player.stream_end_handler(chat_id)
        await query.message.delete()
        if res and res != "EMPTY":
            msg = await client.send_photo(chat_id, photo=res['info'].get('thumbnail'), caption=player.format_playing_message(res['info'], res['by']), reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
    # ... (pause/resume kısımları aynı)
