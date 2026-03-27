from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
import config, asyncio
from database import add_served_chat

PREFIXES = ["/", "."]
playing_messages = {} # Mesaj kirliliğini önlemek için takip

# YETKİ KONTROLÜ
async def has_voice_perms(client, chat_id, user_id):
    if user_id in config.SUDO_USERS: return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except: return False

@Client.on_message(filters.command(["play", "oynat"], prefixes=PREFIXES) & filters.group)
async def play_command(client, message):
    await add_served_chat(message.chat.id)
    chat_id = message.chat.id
    
    # ASİSTAN KONTROL VE ZORLA DAVET
    try:
        await client.get_chat_member(chat_id, "PiMusicAssistan") 
    except:
        m_invite = await message.reply_text("🕵️ **Asistan grupta yok!** Davet ediliyor... 🚀")
        try:
            from main import userbot
            link = await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(link)
            await m_invite.edit("✅ **Asistan katıldı!** İşleme devam ediliyor... ✨")
        except:
            return await m_invite.edit("❌ **@PiMusicAssistan katılamadı.** Lütfen manuel ekleyin! 🛠️")

    if len(message.command) < 2: 
        return await message.reply("🔍 **Şarkı adı yazmalısın!**")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply("🔍 **Aranıyor...** ⏳")
    
    try:
        song_info = search_youtube(query)
        requested_by = message.from_user.mention
        res = await player.add_to_queue_or_play(chat_id, song_info, requested_by)
        
        # Eski mesajı sil
        if chat_id in playing_messages:
            try: await playing_messages[chat_id].delete()
            except: pass

        await m.delete()
        
        # SoundCloud thumbnail kontrolü
        thumb = song_info.get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"

        if res == "FULL":
            await message.reply("⚠️ **Kuyruk dolu!** (Maksimum 5 şarkı). 🛑")
        elif res == "PLAYING":
            try:
                msg = await message.reply_photo(photo=thumb, caption=player.format_playing_message(song_info, requested_by), reply_markup=player.get_player_ui())
            except:
                msg = await message.reply_text(player.format_playing_message(song_info, requested_by), reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
        else:
            msg = await message.reply_photo(photo=thumb, caption=f"✅ **{song_info['title']}** kuyruğa eklendi!\n👤 **Talep:** {requested_by}\n🔢 **Sıra:** {len(player.music_queue[chat_id])}", reply_markup=player.get_player_ui())
            playing_messages[chat_id] = msg
                
    except NoActiveGroupCall: await m.edit("❌ Önce **Sesli Sohbeti** açmalısın! 🎙️")
    except Exception as e: await m.edit(f"❌ **Hata:** {e}")

# KUYRUK LİSTESİ
@Client.on_message(filters.command(["que", "list"], prefixes=PREFIXES) & filters.group)
async def queue_command(client, message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue or not player.music_queue[chat_id]:
        return await message.reply("📭 **Kuyruk şu an boş.**")
    text = "🎼 **Güncel Kuyruk Listesi** 🎼\n\n"
    for i, s in enumerate(player.music_queue[chat_id]):
        prefix = "▶️ **Şu an:** " if i == 0 else f"**{i}.** "
        text += f"{prefix}{s['info']['title']} | 👤 {s['by']}\n"
    await message.reply(text, disable_web_page_preview=True)

# RELOAD KOMUTU
@Client.on_message(filters.command("reload", prefixes=PREFIXES) & filters.group)
async def reload_cmd(client, message):
    await client.get_chat_administrators(message.chat.id)
    await message.reply("✅ **Yönetici listesi güncellendi! Önbellek temizlendi.** 🧹")

# DURDUR / BİTİR KOMUTLARI
@Client.on_message(filters.command(["stop", "dur", "end", "bitir"], prefixes=PREFIXES) & filters.group)
async def control_cmd(client, message):
    if not await has_voice_perms(client, message.chat.id, message.from_user.id):
        return await message.reply(f"❌ {message.from_user.mention}, yetkiniz yok! 🧐")
    
    cmd = message.command[0]
    if cmd in ["stop", "dur"]:
        try: await player.call.pause_stream(message.chat.id); await message.reply("⏸ **Durduruldu.**")
        except: pass
    else:
        player.music_queue.pop(message.chat.id, None)
        try:
            await player.call.leave_group_call(message.chat.id)
            await message.reply(f"⏹ Müzik {message.from_user.mention} tarafından bitirildi. 🧹")
        except: pass

# 🎮 ÇALIŞAN IKONLAR (BUTONLAR)
@Client.on_callback_query()
async def callbacks(client, query):
    chat_id = query.message.chat.id
    if not await has_voice_perms(client, chat_id, query.from_user.id):
        return await query.answer("❌ Yetkiniz yok!", show_alert=True)
    
    data = query.data
    try:
        if data == "pause": await player.call.pause_stream(chat_id); await query.answer("⏸ Durduruldu.")
        elif data == "resume": await player.call.resume_stream(chat_id); await query.answer("▶️ Devam ediyor.")
        elif data == "end":
            player.music_queue.pop(chat_id, None)
            await player.call.leave_group_call(chat_id)
            await query.message.delete()
            await client.send_message(chat_id, f"⏹ Müzik {query.from_user.mention} tarafından bitirildi. 🧹")
        elif data == "skip":
            res = await player.stream_end_handler(chat_id)
            await query.message.delete()
            if res and res != "EMPTY":
                thumb = res['info'].get('thumbnail') or "https://telegra.ph/file/69204068595f57731936c.jpg"
                msg = await client.send_photo(chat_id, photo=thumb, caption=player.format_playing_message(res['info'], res['by']), reply_markup=player.get_player_ui())
                playing_messages[chat_id] = msg
    except: pass
