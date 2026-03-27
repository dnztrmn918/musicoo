from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import AudioPiped
import config
from database import add_served_chat

async def has_voice_perms(client, chat_id, user_id):
    if user_id in config.SUDO_USERS: return True
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_command(client, message):
    await add_served_chat(message.chat.id)
    if len(message.command) < 2: return await message.reply("Şarkı adı girin.")
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 Aranıyor...")
    try:
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(message.chat.id, song_info, message.from_user.mention)
        if res == "FULL": await m.edit("⚠️ Kuyruk dolu (Maks 5).")
        elif res == "PLAYING":
            await m.delete()
            await message.reply(player.format_playing_message(song_info, message.from_user.mention), reply_markup=player.get_player_ui(), disable_web_page_preview=True)
        else: await m.edit(f"✅ {song_info['title']} listeye eklendi.")
    except NoActiveGroupCall: await m.edit("❌ Önce sesli sohbeti başlatın.")
    except Exception as e: await m.edit(f"Hata: {e}")

@Client.on_message(filters.command(["stop", "dur", "end", "bitir"]) & filters.group)
async def control_command(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id):
        return await message.reply(f"Üzgünüm {message.from_user.mention}, yetkiniz yok.", reply_to_message_id=message.id)
    chat_id = message.chat.id
    if message.command[0] in ["end", "bitir"]: player.music_queue.pop(chat_id, None)
    try:
        await player.call.leave_group_call(chat_id)
        await message.reply("⏹ İşlem başarılı.")
    except: pass

@Client.on_message(filters.command(["que", "list"]) & filters.group)
async def queue_command(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue: return await message.reply("Kuyruk boş.")
    text = "🎵 **Kuyruk:**\n\n"
    for i, s in enumerate(player.music_queue[chat_id]):
        text += f"{'▶️' if i==0 else str(i)+'.'} {s['info']['title']}\n"
    await message.reply(text, disable_web_page_preview=True)

@Client.on_callback_query()
async def callbacks(client, query):
    if not await has_voice_perms(client, query.message.chat.id, query.from_user.id):
        return await query.answer("Yetkiniz yok!", show_alert=True)
    # (Buraya önceki callback mantığını ekle)
