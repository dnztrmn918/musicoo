from pyrogram import Client, filters
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import AudioPiped
import config
from database import add_served_chat

PREFIXES = ["/", "."]

@Client.on_message(filters.command(["play", "oynat"], prefixes=PREFIXES) & filters.group)
async def play_command(client, message):
    await add_served_chat(message.chat.id) # Grubu veritabanına kaydeder
    
    if len(message.command) < 2:
        return await message.reply_text("Lütfen oynatmak için bir şarkı ismi girin.")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 Şarkı aranıyor...")
    
    try:
        song_info = search_youtube(query)
        requested_by = message.from_user.mention
        
        try:
            status = await player.add_to_queue_or_play(message.chat.id, song_info, requested_by)
            
            if status == "FULL":
                return await status_msg.edit_text("⚠️ Kuyruk dolu! Lütfen yeni şarkı eklemek için sıranın boşalmasını bekleyin. (Maksimum 5 şarkı)")
            elif status == "PLAYING":
                await status_msg.delete()
                await message.reply_text(
                    text=player.format_playing_message(song_info, requested_by),
                    reply_markup=player.get_player_ui(),
                    disable_web_page_preview=True
                )
            elif status == "QUEUED":
                sira = len(player.music_queue[message.chat.id]) - 1
                await status_msg.edit_text(f"✅ **{song_info['title']}** listeye eklendi! (Sıranız: {sira})")
                
        except NoActiveGroupCall:
            await status_msg.edit_text("❌ Lütfen önce grupta bir **Sesli Sohbet (Voice Chat) başlatın**.")
            if message.chat.id in player.music_queue:
                player.music_queue.pop(message.chat.id, None)
                
    except Exception as e:
        await status_msg.edit_text(f"❌ Bir hata oluştu: {str(e)}")

@Client.on_message(filters.command(["stop", "dur"], prefixes=PREFIXES) & filters.group)
async def pause_command(client, message):
    try:
        await player.call.pause_stream(message.chat.id)
        await message.reply_text("⏸ Müzik duraklatıldı. (Devam etmek için panelden oynat butonuna basın)")
    except Exception:
        await message.reply_text("Şu an duraklatılacak bir müzik çalmıyor.")

@Client.on_message(filters.command(["end", "bitir"], prefixes=PREFIXES) & filters.group)
async def end_command(client, message):
    chat_id = message.chat.id
    if chat_id in player.music_queue:
        player.music_queue.pop(chat_id, None)
    try:
        await player.call.leave_group_call(chat_id)
        await message.reply_text("⏹ Müzik tamamen bitirildi, liste temizlendi ve asistan odadan ayrıldı.")
    except Exception:
        pass

@Client.on_message(filters.command(["que", "list"], prefixes=PREFIXES) & filters.group)
async def queue_command(client, message):
    if message.from_user.id not in config.SUDO_USERS:
        return await message.reply_text("❌ Bu komutu sadece Sudo kullanıcılar kullanabilir.")
        
    chat_id = message.chat.id
    if chat_id not in player.music_queue or not player.music_queue[chat_id]:
        return await message.reply_text("Sırada bekleyen hiçbir şarkı yok.")
        
    text = "🎵 **Kuyruktaki Şarkılar:**\n\n"
    for i, song in enumerate(player.music_queue[chat_id]):
        if i == 0:
            text += f"▶️ **Şu an çalan:** {song['info']['title']} ({song['by']})\n"
        else:
            text += f"{i}. {song['info']['title']} ({song['by']})\n"
            
    await message.reply_text(text, disable_web_page_preview=True)

@Client.on_callback_query()
async def callbacks(client, CallbackQuery):
    chat_id = CallbackQuery.message.chat.id
    data = CallbackQuery.data

    try:
        if data == "pause":
            await player.call.pause_stream(chat_id)
            await CallbackQuery.answer("Müzik duraklatıldı ⏸")
        elif data == "resume":
            await player.call.resume_stream(chat_id)
            await CallbackQuery.answer("Müzik devam ediyor ▶️")
        elif data == "end":
            if chat_id in player.music_queue:
                player.music_queue.pop(chat_id, None)
            await player.call.leave_group_call(chat_id)
            await CallbackQuery.answer("Müzik bitirildi ⏹")
            await CallbackQuery.message.delete()
        elif data == "skip":
            if chat_id in player.music_queue and len(player.music_queue[chat_id]) > 1:
                player.music_queue[chat_id].pop(0) 
                next_song = player.music_queue[chat_id][0]
                await player.call.change_stream(chat_id, AudioPiped(next_song["info"]["url"]))
                await CallbackQuery.answer("Sıradaki şarkıya geçildi ⏭")
                await CallbackQuery.message.edit_text(
                    text=player.format_playing_message(next_song["info"], next_song["by"]),
                    reply_markup=player.get_player_ui()
                )
            else:
                if chat_id in player.music_queue:
                    player.music_queue.pop(chat_id, None)
                await player.call.leave_group_call(chat_id)
                await CallbackQuery.answer("Sırada başka şarkı yok, asistan ayrıldı ⏹")
                await CallbackQuery.message.delete()
    except Exception as e:
        await CallbackQuery.answer(f"Hata: {str(e)}", show_alert=True)
