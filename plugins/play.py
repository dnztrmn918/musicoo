from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import AudioPiped
import config
from database import add_served_chat

PREFIXES = ["/", "."]
playing_messages = {} # Eski mesajları takip etmek için

async def has_voice_perms(client, chat_id, user_id):
    if user_id in config.SUDO_USERS: return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except: return False

@Client.on_message(filters.command(["play", "oynat"], prefixes=PREFIXES) & filters.group)
async def play_command(client, message):
    await add_served_chat(message.chat.id)
    if len(message.command) < 2: return await message.reply("Şarkı adı girin.")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 Aranıyor...")
    
    try:
        song_info = search_youtube(query)
        requested_by = message.from_user.mention
        res = await player.add_to_queue_or_play(message.chat.id, song_info, requested_by)
        
        if res == "FULL":
            await m.edit("⚠️ Kuyruk dolu (Maks 5).")
        else:
            # Eski mesajı silme işlemi
            if message.chat.id in playing_messages:
                try: await playing_messages[message.chat.id].delete()
                except: pass
            
            await m.delete()
            if res == "PLAYING":
                msg = await message.reply_photo(
                    photo=song_info['thumbnail'],
                    caption=player.format_playing_message(song_info, requested_by),
                    reply_markup=player.get_player_ui()
                )
                playing_messages[message.chat.id] = msg
            else:
                sira = len(player.music_queue[message.chat.id])
                msg = await message.reply_photo(
                    photo=song_info['thumbnail'],
                    caption=f"✅ **{song_info['title']}** kuyruğa eklendi!\n👤 **Talep Eden:** {requested_by}\n🔢 **Sıra:** {sira}",
                    reply_markup=player.get_player_ui()
                )
                playing_messages[message.chat.id] = msg
                
    except NoActiveGroupCall: await m.edit("❌ Önce sesli sohbeti başlatın.")
    except Exception as e: await m.edit(f"Hata: {e}")

@Client.on_message(filters.command(["que", "list"], prefixes=PREFIXES) & filters.group)
async def queue_command(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue: return await message.reply("Kuyruk boş.")
    
    text = "🎵 **Mevcut Kuyruk:**\n\n"
    for i, s in enumerate(player.music_queue[chat_id]):
        prefix = "▶️ **Şu an:** " if i == 0 else f"{i}. "
        text += f"{prefix}{s['info']['title']} | 👤 {s['by']}\n"
    await message.reply(text, disable_web_page_preview=True)

# --- BUTONLARIN VE STOP/END KOMUTLARININ TAMAMI BURADA ---
@Client.on_callback_query()
async def callback_handler(client, query):
    chat_id = query.message.chat.id
    if not await has_voice_perms(client, chat_id, query.from_user.id):
        return await query.answer("Yetkiniz yok!", show_alert=True)

    data = query.data
    try:
        if data == "pause":
            await player.call.pause_stream(chat_id)
            await query.answer("Duraklatıldı.")
        elif data == "resume":
            await player.call.resume_stream(chat_id)
            await query.answer("Devam ediyor.")
        elif data == "end":
            player.music_queue.pop(chat_id, None)
            await player.call.leave_group_call(chat_id)
            await query.message.delete()
            await client.send_message(chat_id, f"⏹ Müzik {query.from_user.mention} tarafından sonlandırıldı.")
        elif data == "skip":
            res = await player.stream_end_handler(chat_id)
            if res == "EMPTY":
                await query.answer("Kuyruk bitti.")
                await query.message.delete()
            elif res:
                await query.message.delete()
                msg = await client.send_photo(chat_id, photo=res['info']['thumbnail'], caption=player.format_playing_message(res['info'], res['by']), reply_markup=player.get_player_ui())
                playing_messages[chat_id] = msg
    except: pass
