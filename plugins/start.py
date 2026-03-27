import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_user, get_served_users, get_served_chats
import player, config

# --- PANEL TASARIMLARI ---
def start_panel(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("🛠️ Komutlar", callback_data="help_main"), 
         InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/dnztrmnn")],
        [InlineKeyboardButton("📢 Resmi Kanal", url="https://t.me/NowaDestek")]
    ])

def help_main_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Müzik Menüsü", callback_data="help_music"),
         InlineKeyboardButton("🏷️ Etiket Menüsü", callback_data="help_tag")],
        [InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="start_menu")]
    ])

def back_to_help_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri Dön", callback_data="help_main")]])

# --- KOMUTLAR ---
@Client.on_message(filters.command(["start"]) & filters.private)
async def start_private(client, message):
    await add_served_user(message.from_user.id)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    start_text = (
        f"👋 **Merhaba {message.from_user.mention}!**\n\n"
        "🎵 **Nowa-Müzik Botu** ile gruplarında yüksek kalitede sesli sohbet yayınları yapabilirsin.\n\n"
        f"📊 **İstatistikler:**\n"
        f"👥 Kullanıcı: `{users}`\n"
        f"💬 Grup: `{chats}`\n\n"
        "Butonları kullanarak detaylı bilgi alabilirsin. ✨"
    )
    await message.reply_text(text=start_text, reply_markup=start_panel(client.me.username))

@Client.on_message(filters.command("reload"))
async def reload_cmd(client, message):
    await message.reply_text("✅ **Sistem ve yönetici listesi başarıyla tazelendi!**")

# --- CALLBACK HANDLER (Buton Fonksiyonları) ---
@Client.on_callback_query()
async def centralized_callbacks(client, query):
    data = query.data
    chat_id = query.message.chat.id

    if data == "start_menu":
        users = len(await get_served_users())
        chats = len(await get_served_chats())
        await query.message.edit_text(
            f"👋 **Ana Menüye Hoş Geldin!**\n\n📊 İstatistikler:\n👥 Kullanıcı: `{users}` | 💬 Grup: `{chats}`",
            reply_markup=start_panel(client.me.username)
        )

    elif data == "help_main":
        await query.message.edit_text(
            "🛠️ **Yardım ve Komutlar**\n\nLütfen öğrenmek istediğin kategoriyi seç:",
            reply_markup=help_main_markup()
        )

    elif data == "help_music":
        music_text = (
            "🎵 **Müzik Komutları**\n\n"
            "• `/play [isim]` : Şarkı başlatır.\n"
            "• `/skip` : Sıradaki şarkıya geçer.\n"
            "• `/dur` : Yayını duraklatır.\n"
            "• `/bitir` : Yayını kapatır ve kuyruğu siler.\n"
            "• `/que` : Kuyruk listesini gösterir."
        )
        await query.message.edit_text(text=music_text, reply_markup=back_to_help_markup())

    elif data == "help_tag":
        tag_text = (
            "🏷️ **Etiketleme Sistemleri**\n\n"
            "• `/tag [mesaj]` : Tüm üyeleri etiketler.\n"
            "• `/gtag` : Günaydın mesajlı etiket.\n"
            "• `/itag` : İyi geceler mesajlı etiket.\n"
            "• `/stag` : Sohbete çağırma mesajı.\n"
            "• `/ktag` : Kurt oyunu çağrısı.\n"
            "• `/cancel` : Aktif işlemi durdurur."
        )
        await query.message.edit_text(text=tag_text, reply_markup=back_to_help_markup())

    # Müzik Buton Fonksiyonları (player.py entegreli)
    elif data == "skip":
        res = await player.stream_end_handler(chat_id)
        await query.message.delete()
        if res and res != "EMPTY":
            await client.send_photo(chat_id, photo=res['info'].get('thumbnail'), caption=player.format_playing_message(res['info'], res['by']), reply_markup=player.get_player_ui())
    
    elif data == "end":
        player.music_queue.pop(chat_id, None)
        try: await player.call.leave_group_call(chat_id)
        except: pass
        await query.message.delete()
        await client.send_message(chat_id, "⏹ **Yayın sonlandırıldı.** 🧹")

    elif data == "pause":
        try: await player.call.pause_stream(chat_id)
        except: pass
        await query.answer("⏸ Durduruldu.")
        
    elif data == "resume":
        try: await player.call.resume_stream(chat_id)
        except: pass
        await query.answer("▶️ Devam ediyor.")

    elif data == "close_stats":
        await query.message.delete()
