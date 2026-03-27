from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import AudioPiped
import config
from database import add_served_chat

PREFIXES = ["/", "."]

async def has_voice_perms(client, chat_id, user_id):
    if user_id in config.SUDO_USERS: return True
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

@Client.on_message(filters.command(["play", "oynat"], prefixes=PREFIXES) & filters.group)
async def play_command(client, message):
    await add_served_chat(message.chat.id)
    if len(message.command) < 2: return await message.reply("Şarkı adı girin.")
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 Şarkı aranıyor...")
    try:
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(message.chat.id, song_info, message.from_user.mention)
        if res == "FULL": await m.edit("⚠️ Kuyruk dolu (Maks 5 şarkı).")
        elif res == "PLAYING":
            await m.delete()
            await message.reply(player.format_playing_message(song_info, message.from_user.mention), reply_markup=player.get_player_ui(), disable_web_page_preview=True)
        else: await m.edit(f"✅ **{song_info['title']}** listeye eklendi.")
    except NoActiveGroupCall: await m.edit("❌ Önce sesli sohbeti başlatın.")
    except Exception as e: await m.edit(f"Hata: {e}")

# STOP / DUR: Şarkıyı olduğu yerde durdurur 
@Client.on_message(filters.command(["stop", "dur"], prefixes=PREFIXES) & filters.group)
async def stop_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id):
        return await message.reply(f"Üzgünüm {message.from_user.mention}, yetkiniz yok.", reply_to_message_id=message.id)
    try:
        await player.call.pause_stream(message.chat.id)
        await message.reply_text("⏸ Müzik duraklatıldı.")
    except: pass

# RESUME / DEVAM: Kaldığı yerden devam ettirir 
@Client.on_message(filters.command(["resume", "devam"], prefixes=PREFIXES) & filters.group)
async def resume_cmd(client, message):
    try:
        await player.call.resume_stream(message.chat.id)
        await message.reply_text("▶️ Müzik kaldığı yerden devam ediyor.")
    except: pass

# END / BİTİR: Sıradakine geçer, yoksa odadan çıkar 
@Client.on_message(filters.command(["end", "bitir"], prefixes=PREFIXES) & filters.group)
async def end_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id):
        return await message.reply(f"Üzgünüm {message.from_user.mention}, yetkiniz yok.", reply_to_message_id=message.id)
    
    result = await player.stream_end_handler(message.chat.id)
    finisher = message.from_user.mention
    
    if result == "EMPTY":
        await message.reply_text(f"⏹ Müzik {finisher} tarafından sonlandırıldı. Kuyruk boş olduğu için asistan ayrıldı.")
    elif result:
        await message.reply_text(f"⏭ Müzik {finisher} tarafından sonlandırıldı. Sıradaki şarkıya geçiliyor...")
        await message.reply(player.format_playing_message(result["info"], result["by"]), reply_markup=player.get_player_ui())

@Client.on_message(filters.command(["que", "list"], prefixes=PREFIXES) & filters.group)
async def queue_command(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue: return await message.reply("Kuyruk boş.")
    text = "🎵 **Mevcut Kuyruk:**\n\n"
    for i, s in enumerate(player.music_queue[chat_id]):
        text += f"{'▶️' if i==0 else str(i)+'.'} {s['info']['title']}\n"
    await message.reply(text, disable_web_page_preview=True)
