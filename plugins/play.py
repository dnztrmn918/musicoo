import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
import player
from search import search_youtube
from plugins.assistant import assistant_join
import config

BOT_NAME = "Pi Müzik"
DEFAULT_LOGO = "plugins/logo.jpg"

async def is_admin(client, chat_id, user_id):
    from database import is_sudo
    if await is_sudo(user_id): return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.privileges and (member.privileges.can_manage_video_chats or member.status.value in ["creator", "administrator"])
    except: return False

@Client.on_message(filters.command(["play", "p", "oynat"]) & filters.group)
async def play_cmd(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("❌ **Şarkı adı veya linki yazmalısın.**")
    
    msg = await message.reply(f"🔍 **{BOT_NAME}** arıyor...")
    try:
        result = search_youtube(query)
        if not result: return await msg.edit("❌ Şarkı bulunamadı.")

        join_status = await assistant_join(client, message.chat.id)
        if join_status is not True: return await msg.edit(f"❌ Asistan hatası: {join_status}")

        status, extra = await player.add_to_queue_or_play(message.chat.id, result, message.from_user.first_name)
        try: await msg.delete()
        except: pass

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

        # 🔥 ŞARKI ÇALARKEN YENİSİ EKLENİRSE BİLGİ YAZDIRIR
        elif status == "QUEUED":
            q_pos = extra
            caption_text = f"⏳ **Kuyruğa Eklendi (Sıra: {q_pos})**\n📌 **Parça:** `{result['title']}`\n👤 **İsteyen:** {message.from_user.first_name}"
            await message.reply_photo(photo=result.get('thumbnail') or DEFAULT_LOGO, caption=caption_text)
            
        elif status == "ERROR":
            await message.reply(f"❌ **Oynatma Hatası:** {extra}")

    except Exception as e:
        await message.reply(f"❌ **Hata:** {str(e)[:50]}")

# --- DURDURMA KOMUTLARI (PAUSE YAPANLAR) ---
@Client.on_message(filters.command(["stop", "dur", "pause", "durdur", "beklet"]) & filters.group)
async def pause_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.pause_stream(message.chat.id):
        await message.reply("⏸ **Müzik duraklatıldı.**")

# --- DEVAM ET KOMUTLARI (RESUME YAPANLAR) ---
@Client.on_message(filters.command(["resume", "devam", "r"]) & filters.group)
async def resume_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if await player.resume_stream(message.chat.id):
        await message.reply("▶️ **Müzik devam ediyor.**")

# --- ATLA / BİTİR KOMUTLARI (SKIP VE END BİRLEŞTİRİLDİ) ---
@Client.on_message(filters.command(["skip", "atla", "next", "n", "end", "bitir", "son"]) & filters.group)
async def skip_end_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    
    # Eğer komut skip ise ekrana atlandığını belirten ufak bir mesaj bırakır.
    if message.command[0] in ["skip", "atla", "next", "n"]:
        await message.reply("⏭ **Geçerli parça atlandı...**")
    
    # 🔥 drop_call yerine %100 ÇALIŞAN stream_end_handler kullanıldı.
    # Görevi: Kuyrukta varsa sıradakine geç, yoksa çıkıp "Yayın Sonlandırıldı" de.
    await player.stream_end_handler(message.chat.id)

@Client.on_message(filters.command(["sil", "temizle", "clear"]) & filters.group)
async def clean_text_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    player.clear_queue_except_current(message.chat.id)
    await message.reply("🗑️ **Kuyruk temizlendi (Çalan hariç).**")

# --- BUTONLAR (METİN KOMUTLARI İLE %100 AYNI İŞLEVİ YAPAR) ---
@Client.on_callback_query(filters.regex("^(pause|resume|skip|end)$"))
async def player_callbacks(client, query: CallbackQuery):
    c_id = query.message.chat.id
    if not await is_admin(client, c_id, query.from_user.id):
        return await query.answer("❌ Yetkin yok.", show_alert=True)

    if query.data == "pause":
        if await player.pause_stream(c_id): await query.answer("⏸ Durduruldu")
    elif query.data == "resume":
        if await player.resume_stream(c_id): await query.answer("▶️ Devam ediyor")
    elif query.data in ["skip", "end"]:
        await query.answer("⏭ İşlem uygulanıyor...")
        # Hem skip hem end butonunda komutla aynı şekilde varsa geçer, yoksa çıkar
        await player.stream_end_handler(c_id)
