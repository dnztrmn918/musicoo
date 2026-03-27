from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from search import search_youtube
from plugins.assistant import assistant_join
import player
import config


# ────────────────────────────────────────────────
#  ŞARKI BAŞLATMA / KUYRUK YÖNETİMİ
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_command(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply("🔍 **Bir şarkı adı veya link belirtin.**")

    waiting = await message.reply("📡 **Asistan ve ses kontrol ediliyor...**")
    join_status = await assistant_join(client, chat_id)
    if join_status == "ADMIN_REQUIRED":
        return await waiting.edit(
            "❌ **Beni yönetici yapın ve 'Davet Bağlantısı Oluşturma' yetkisini verin.**"
        )
    elif not join_status:
        return await waiting.edit("❌ **Asistan bağlantısı kurulamadı.**")

    try:
        query = message.text.split(None, 1)[1]
        song_info = search_youtube(query)
        status = await player.add_to_queue_or_play(chat_id, song_info, message.from_user.mention)
        await waiting.delete()

        if status == "FULL":
            return await message.reply(
                "⚠️ **Kuyruk dolu!** Maksimum 5 şarkı eklenebilir.\n"
                "🎧 Şarkılardan bazıları bitince tekrar deneyin.", 
                quote=True
            )
        elif status == "ERROR":
            return await message.reply("❌ **Yayın başlatılamadı.**")

        thumb = song_info.get("thumbnail") or "[telegra.ph](https://telegra.ph/file/69204068595f57731936c.jpg)"
        await message.reply_photo(
            photo=thumb,
            caption=player.format_playing_message(song_info, message.from_user.mention),
            reply_markup=player.get_player_ui(),
        )
    except Exception as e:
        await waiting.edit(f"❌ **Hata:** `{e}`")


# ────────────────────────────────────────────────
#  KOMUTLAR
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message):
    res = await player.stream_end_handler(message.chat.id)
    if res == "EMPTY":
        await message.reply("⏹ **Kuyruk bitti.**")
    elif isinstance(res, dict):
        await message.reply(f"⏭ **Sıradaki:** `{res['info']['title']}`")


@Client.on_message(filters.command(["stop", "dur", "pause"]) & filters.group)
async def stop_cmd(client, message):
    try:
        await player.call.pause_stream(message.chat.id)
        await message.reply("⏸ **Duraklatıldı.**")
    except:
        pass


@Client.on_message(filters.command(["resume", "devam"]) & filters.group)
async def resume_cmd(client, message):
    try:
        await player.call.resume_stream(message.chat.id)
        await message.reply("▶️ **Devam ediyor.**")
    except:
        pass


@Client.on_message(filters.command(["end", "bitir"]) & filters.group)
async def end_cmd(client, message):
    player.clear_queue(message.chat.id)
    try:
        await player.call.leave_group_call(message.chat.id)
        await message.reply("⏹ **Yayın bitti.**")
    except:
        pass


# ────────────────────────────────────────────────
#  KUYRUK GÖSTER / TEMİZLE
# ────────────────────────────────────────────────
@Client.on_message(filters.command(["que", "kuyruk"]) & filters.group)
async def queue_cmd(client, message):
    text = player.format_queue(message.chat.id)
    await message.reply(text)


@Client.on_message(filters.command(["sil"]) & filters.group)
async def clear_or_delete_queue(client, message):
    chat_id = message.chat.id
    if len(message.command) == 1:
        if chat_id not in player.music_queue or not player.music_queue[chat_id]:
            return await message.reply("📭 **Kuyruk boş.**")
        player.clear_queue(chat_id)
        return await message.reply("🧹 **Tüm kuyruk temizlendi.**")

    try:
        index = int(message.command[1]) - 1
        removed = player.remove_from_queue(chat_id, index)
        if removed:
            await message.reply(f"🗑️ **Silindi:** `{removed['info']['title']}`")
        else:
            await message.reply("⚠️ Geçersiz sıra numarası.")
    except ValueError:
        await message.reply("❌ Geçerli bir sayı belirtin.")
