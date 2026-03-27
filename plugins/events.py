from pyrogram import Client, filters
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
import player
import config

# 🎤 SESLİ SOHBET BAŞLATILDIĞINDA MESAJ GÖNDERME
@Client.on_message(filters.video_chat_started)
async def vc_started(client, message):
    await message.reply_text(
        "✨ **Sesli Sohbet Başarıyla Başlatıldı!**\n\n"
        "🎵 Müzik yayını yapılmaya hazır. `/play` komutu ile kulakların pasını silebiliriz! 🎧"
    )

# ➕ BOT BİR GRUBA EKLENDİĞİNDE (Karşılama ve Log)
@Client.on_message(filters.new_chat_members)
async def welcome_and_log(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            # Gruba karşılama mesajı
            await message.reply_text(
                "👋 **Beni gruba aldığın için teşekkürler!**\n\n"
                "🎵 Yetki vererek kullanım adımlarını takip edip kullanmaya başlayabilirsiniz.\n"
                "🛡️ Lütfen 'Mesajları Sil' ve 'Sesli Sohbet Yönet' yetkilerimi verin! ✨"
            )
            
            # Log grubuna bildirim gönder
            if config.LOG_GROUP_ID:
                chat = message.chat
                log_text = (
                    "➕ **Yeni Bir Gruba Eklendim!**\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏷 **Grup Adı:** `{chat.title}`\n"
                    f"🆔 **Grup ID:** `{chat.id}`\n"
                    f"👤 **Ekleyen:** {message.from_user.mention if message.from_user else 'Bilinmiyor'}\n"
                    "━━━━━━━━━━━━━━━━━━━━"
                )
                try:
                    await client.send_message(config.LOG_GROUP_ID, log_text)
                except Exception as e:
                    print(f"Log gönderme hatası: {e}")

# ➖ BOT GRUPTAN ÇIKARILDIĞINDA (Log)
@Client.on_message(filters.left_chat_member)
async def bot_removed_log(client, message):
    if message.left_chat_member.id == client.me.id:
        if config.LOG_GROUP_ID:
            chat = message.chat
            log_text = (
                "➖ **Bir Gruptan Çıkarıldım!**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🏷 **Grup Adı:** `{chat.title}`\n"
                f"🆔 **Grup ID:** `{chat.id}`\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            try:
                await client.send_message(config.LOG_GROUP_ID, log_text)
            except Exception as e:
                print(f"Log gönderme hatası: {e}")

# 🏁 ŞARKI BİTİŞ YÖNETİCİSİ
async def on_stream_end_handler(client, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        result = await player.stream_end_handler(chat_id)
        
        # main içindeki bot nesnesini güvenli bir şekilde çekiyoruz
        from main import bot 
        
        if bot.is_connected: # Bağlantı aktif mi kontrolü
            if result == "EMPTY":
                await bot.send_message(
                    chat_id, 
                    "ℹ️ **Kuyrukta herhangi bir parça yok, asistan sesli sohbetten ayrılıyor.** 👋"
                )
            elif result:
                # SoundCloud thumbnail kontrolü
                thumb = result["info"].get("thumbnail") or "https://telegra.ph/file/69204068595f57731936c.jpg"
                try:
                    await bot.send_photo(
                        chat_id,
                        photo=thumb,
                        caption=player.format_playing_message(result["info"], result["by"]),
                        reply_markup=player.get_player_ui()
                    )
                except:
                    # Fotoğraf gönderilemezse sadece mesaj at
                    await bot.send_message(
                        chat_id,
                        caption=player.format_playing_message(result["info"], result["by"]),
                        reply_markup=player.get_player_ui()
                    )
