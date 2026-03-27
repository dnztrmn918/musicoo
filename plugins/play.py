from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import AudioPiped
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
    
    # ASİSTAN KONTROLÜ
    try:
        await client.get_chat_member(chat_id, "PiMusicAssistan") # Asistanın tam kullanıcı adını yazın
    except:
        m_invite = await message.reply_text("🕵️ **Asistan hesap grupta yok!** Çağırmaya çalışıyorum...")
        try:
            from main import userbot
            link = await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(link)
            await m_invite.edit("✅ Asistan gruba katıldı!")
        except:
            return await m_invite.edit("❌ **@PiMusicAssistan katılamadı!** Manuel ekleyip yetki vermelisiniz.")

    if len(message.command) < 2: return await message.reply("🔍 Lütfen şarkı adı girin.")
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 **Aranıyor...** ⏳")
    
    try:
        song_info = search_youtube(query)
        res = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        
        if message.chat.id in playing_messages:
            try: await playing_messages[message.chat.id].delete()
            except: pass

        if res == "FULL": await m.edit("⚠️ **Kuyruk dolu!** (Maksimum 5 şarkı limitine ulaşıldı.)")
        elif res == "PLAYING":
            await m.delete()
            msg = await message.reply_photo(photo=song_info['thumbnail'], caption=player.format_playing_message(song_info, message.from_user.mention), reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
        else:
            await m.delete()
            msg = await message.reply_photo(photo=song_info['thumbnail'], caption=f"✅ **{song_info['title']}** kuyruğa eklendi!\n🔢 **Sıra:** {len(player.music_queue[chat_id])}\n👤 **Talep Eden:** {message.from_user.mention}", reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
                
    except NoActiveGroupCall: await m.edit("❌ Önce **Sesli Sohbeti** başlatmalısın!")
    except Exception as e: await m.edit(f"❌ Hata: {e}")

@Client.on_message(filters.command(["que", "list"]) & filters.group)
async def queue_command(client, message):
    if message.chat.id not in player.music_queue: return await message.reply("📭 Kuyrukta parça yok.")
    text = "🎼 **Mevcut Kuyruk** 🎼\n\n"
    for i, s in enumerate(player.music_queue[message.chat.id]):
        text += f"{'🔥' if i==0 else str(i)+'.'} {s['info']['title']} | 👤 {s['by']}\n"
    await message.reply(text, disable_web_page_preview=True)

@Client.on_message(filters.command("reload") & filters.group)
async def reload_cmd(client, message):
    await client.get_chat_administrators(message.chat.id)
    await message.reply("✅ **Yönetici listesi güncellendi! Önbellek temizlendi.** 🧹")

@Client.on_message(filters.command(["stop", "dur", "end", "bitir"]) & filters.group)
async def control_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id):
        return await message.reply(f"❌ Üzgünüm {message.from_user.mention}, senin **yetkin yok!** 🧐", reply_to_message_id=message.id)
    
    cmd = message.command[0]
    if cmd in ["stop", "dur"]:
        try: await player.call.pause_stream(message.chat.id); await message.reply("⏸ Duraklatıldı.")
        except: pass
    else:
        res = await player.stream_end_handler(message.chat.id)
        mention = message.from_user.mention
        if res == "EMPTY": await message.reply(f"⏹ Müzik {mention} tarafından sonlandırıldı. Kuyruk boş olduğu için asistan ayrıldı.")
        elif res: await message.reply(f"⏭ Müzik {mention} tarafından sonlandırıldı. Sıradaki parçaya geçiliyor...")

@Client.on_callback_query()
async def callbacks(client, query):
    chat_id = query.message.chat.id
    if not await has_voice_perms(client, chat_id, query.from_user.id):
        return await query.answer("❌ Yetkin yok!", show_alert=True)
    
    data = query.data
    if data == "pause": await player.call.pause_stream(chat_id); await query.answer("⏸ Durduruldu.")
    elif data == "resume": await player.call.resume_stream(chat_id); await query.answer("▶️ Devam ediyor.")
    elif data == "end":
        player.music_queue.pop(chat_id, None)
        await player.call.leave_group_call(chat_id)
        await query.message.delete()
        await client.send_message(chat_id, f"⏹ Müzik {query.from_user.mention} tarafından sonlandırıldı. 🧹")
    elif data == "skip":
        res = await player.stream_end_handler(chat_id)
        await query.message.delete()
        if res and res != "EMPTY":
            msg = await client.send_photo(chat_id, photo=res['info']['thumbnail'], caption=player.format_playing_message(res['info'], res['by']), reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
