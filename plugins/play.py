import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

BOT_NAME = "Pi Müzik"
DEFAULT_LOGO = "plugins/logo.jpg"
CMD_PREFIXES = ["/", "!", "."]

async def is_admin(client, chat_id, user_id):
    from database import is_sudo
    if await is_sudo(user_id): return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and (member.privileges.can_manage_video_chats or member.status.value in ["creator", "administrator"])
    except: return False

@Client.on_message(filters.command(["play", "p", "oynat"], prefixes=CMD_PREFIXES) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("❌ **Şarkı adı veya linki yazmalısın.**")
    
    msg = await message.reply(f"🔍 **{BOT_NAME}** arıyor ve indiriyor...")
    try:
        result = search_youtube(query)
        if not result: return await msg.edit("❌ Şarkı bulunamadı. Lütfen başka bir isimle ara.")

        join_status = await assistant_join(client, message.chat.id)
        if join_status is not True: return await msg.edit(f"❌ Asistan gruba/sese katılamadı: {join_status}")

        status, extra = await player.add_to_queue_or_play(message.chat.id, result, message.from_user.first_name)
        
        try: await msg.delete()
        except: pass

        # 🔥 YENİ: KUYRUK LİMİTİ KONTROLÜ
        if status == "FULL":
            return await message.reply("⚠️ **Kuyruk limiti doldu!**\nKuyruğa en fazla 5 şarkı eklenebilir. Şarkılar çaldıkça yer açılacaktır.")

        if status == "PLAYING":
            if message.chat.id in player.last_message_ids:
                try: await client.delete_messages(message.chat.id, player.last_message_ids[message.chat.id])
                except: pass
            
            sent_p = await message.reply_photo(
                photo=result.get('thumbnail') or DEFAULT_LOGO,
                caption=player.format_playing_message(result, message.from_user.first_name),
                reply_markup=player.get_player_ui()
            )
            player.last_message_ids[message.chat.id] = sent_p.id

        elif status == "QUEUED":
            q_pos = extra
            caption_text = f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n📌 **Parça:** `{result['title']}`\n👤 **İsteyen:** {message.from_user.first_name}"
            await message.reply_photo(photo=result.get('thumbnail') or DEFAULT_LOGO, caption=caption_text)
            
        elif status == "ERROR":
            await message.reply(f"❌ **Oynatma Hatası:** {extra}")

    except Exception as e:
        await message.reply(f"❌ **Beklenmedik Hata:** {str(e)[:50]}")

@Client.on_message(filters.command(["que", "list", "kuyruk", "liste"], prefixes=CMD_PREFIXES) & filters.group)
async def queue_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in player.music_queue or not player.music_queue[chat_id]:
        return await message.reply("📂 **Kuyrukta şu an hiç şarkı yok.**")
    
    queue = player.music_queue[chat_id]
    text = f"📜 **{BOT_NAME} Kuyruk Listesi**\n\n"
    
    current = queue[0]
    text += f"🎧 **Şu An Çalan:**\n📌 `{current['info']['title']}`\n⏳ Süre: `{current['info'].get('duration', 'Bilinmiyor')}` | 👤 İsteyen: {current['by']}\n\n"
    
    if len(queue) > 1:
        text += "⏳ **Sıradakiler:**\n"
        for i, song in enumerate(queue[1:], start=1):
            text += f"**{i}.** `{song['info']['title']}`\n├ ⏳ `{song['info'].get('duration', 'Bilinmiyor')}` | 👤 {song['by']}\n\n"
    else:
        text += "📭 **Sırada bekleyen başka şarkı yok.**"
        
    try:
        if os.path.exists("que.png"): await message.reply_photo(photo="que.png", caption=text)
        else: await message.reply(text)
    except: await message.reply(text)

@Client.on_message(filters.command(["stop", "dur", "pause", "durdur"], prefixes=CMD_PREFIXES) & filters.group)
async def pause_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.pause_stream(message.chat.id): await message.reply("⏸ **Müzik duraklatıldı.**")

@Client.on_message(filters.command(["devam", "resume", "r"], prefixes=CMD_PREFIXES) & filters.group)
async def resume_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.resume_stream(message.chat.id): await message.reply("▶️ **Müzik kaldığı yerden devam ediyor.**")

@Client.on_message(filters.command(["skip", "geç", "atla"], prefixes=CMD_PREFIXES) & filters.group)
async def skip_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    await player.stream_end_handler(message.chat.id, action="skip")

@Client.on_message(filters.command(["end", "bitir", "son"], prefixes=CMD_PREFIXES) & filters.group)
async def end_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    await player.stream_end_handler(message.chat.id, action="end")

# 🔥 YENİ: GELİŞMİŞ SİL KOMUTU
@Client.on_message(filters.command(["sil", "temizle", "clear"], prefixes=CMD_PREFIXES) & filters.group)
async def clean_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    
    # Eğer "/sil 1" gibi bir numara yazıldıysa
    if len(message.command) > 1:
        try:
            index = int(message.command[1])
            if index <= 0:
                return await message.reply("❌ Lütfen 1 veya daha büyük bir sayı girin (Örn: `/sil 1`).")
            
            removed_title = player.remove_from_queue(message.chat.id, index)
            if removed_title:
                await message.reply(f"🗑️ **Sıradaki {index}. parça silindi:** `{removed_title}`")
            else:
                await message.reply(f"❌ **Kuyrukta {index}. sırada bir şarkı bulunamadı.**")
        except ValueError:
            await message.reply("❌ Lütfen silmek istediğiniz şarkının numarasını doğru girin (Örn: `/sil 1`).")
    else:
        # Sadece "/sil" yazıldıysa tüm kuyruğu temizle
        player.clear_queue_except_current(message.chat.id)
        await message.reply("🗑️ **Kuyruk tamamen temizlendi (Çalan parça hariç).**")

@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def player_callbacks(client, query: CallbackQuery):
    c_id = query.message.chat.id
    if not await is_admin(client, c_id, query.from_user.id):
        return await query.answer("❌ Bu işlemi yapmak için yetkiniz yok.", show_alert=True)

    try:
        if query.data == "pause":
            if await player.pause_stream(c_id): await query.answer("⏸ Şarkı Durduruldu")
        elif query.data == "resume":
            if await player.resume_stream(c_id): await query.answer("▶️ Şarkı Devam Ediyor")
        elif query.data == "skip":
            await query.answer("⏭ Sıradaki Parçaya Geçiliyor...")
            await player.stream_end_handler(c_id, action="skip")
        elif query.data == "end":
            await query.answer("⏹ Yayın Kapatılıyor...")
            await player.stream_end_handler(c_id, action="end")
    except FloodWait as e:
        await asyncio.sleep(e.value)
