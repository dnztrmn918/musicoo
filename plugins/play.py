from pyrogram import Client, filters
from search import search_youtube
import player
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import AudioPiped # Sıradaki şarkıya geçiş için eklendi

PREFIXES = ["/", "."]

@Client.on_message(filters.command(["play", "oynat"], prefixes=PREFIXES) & filters.group)
async def play_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Lütfen oynatmak için bir şarkı ismi girin.")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 Şarkı aranıyor...")
    
    try:
        song_info = search_youtube(query)
        requested_by = message.from_user.mention
        
        # SESLİ SOHBET KONTROLÜ
        try:
            is_playing = await player.add_to_queue_or_play(message.chat.id, song_info, requested_by)
            
            if is_playing:
                await status_msg.delete()
                if song_info['thumbnail']:
                    await message.reply_photo(
                        photo=song_info['thumbnail'],
                        caption=player.format_playing_message(song_info, requested_by),
                        reply_markup=player.get_player_ui()
                    )
                else:
                    await message.reply_text(
                        text=player.format_playing_message(song_info, requested_by),
                        reply_markup=player.get_player_ui(),
                        disable_web_page_preview=True
                    )
            else:
                await status_msg.edit_text(f"✅ **{song_info['title']}** kuyruğa eklendi!")
                
        except NoActiveGroupCall:
            await status_msg.edit_text("❌ **Müzik çalamıyorum!**\nLütfen önce grupta bir **Sesli Sohbet (Voice Chat) başlatın** ve komutu tekrar deneyin.")
            if message.chat.id in player.music_queue:
                player.music_queue.pop(message.chat.id, None)
                
    except Exception as e:
        await status_msg.edit_text(f"❌ Bir hata oluştu: {str(e)}")

@Client.on_message(filters.command(["stop", "dur", "end", "bitir"], prefixes=PREFIXES) & filters.group)
async def stop_command(client, message):
    chat_id = message.chat.id
    if chat_id in player.music_queue:
        player.music_queue.pop(chat_id, None)
        
    try:
        await player.call.leave_group_call(chat_id)
        await message.reply_text("⏹ Müzik durduruldu ve sesli sohbetten çıkıldı.")
    except NoActiveGroupCall:
        await message.reply_text("Zaten aktif bir sesli sohbette değilim veya sohbet kapalı.")
    except Exception as e:
        await message.reply_text(f"Bir sorun oluştu: {str(e)}")

@Client.on_message(filters.command(["asistan", "kontrol"], prefixes=PREFIXES) & filters.group)
async def check_assistant(client, message):
    try:
        await message.reply_text("✅ Asistan sistemi kodlara başarıyla entegre edildi. Lütfen Koyeb loglarını kontrol edin.")
    except Exception as e:
        await message.reply_text(f"❌ Bir sorun var: {e}")

# BUTONLARI AKTİFLEŞTİREN YENİ KISIM
@Client
