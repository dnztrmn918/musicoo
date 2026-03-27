import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_user, get_served_users, get_served_chats
import player, config

LOGO_PATH = os.path.join(os.getcwd(), "plugins", "logo.jpg")

def start_panel(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("🛠️ Komutlar", callback_data="help_main"), InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/dnztrmnn")],
        [InlineKeyboardButton("📢 Resmi Kanal", url="https://t.me/NowaDestek")]
    ])

def help_main_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Müzik Menüsü", callback_data="help_music"), InlineKeyboardButton("🏷️ Etiket Menüsü", callback_data="help_tag")],
        [InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="start_menu")]
    ])

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await add_served_user(message.from_user.id)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    caption = f"👋 **Merhaba {message.from_user.mention}!**\n\n🎵 **Nowa-Müzik Botuna Hoş Geldin.**\n\n📊 **İstatistikler:**\n👥 Kullanıcı: `{users}`\n💬 Grup: `{chats}`\n\nLütfen aşağıdaki butonları kullanın."
    
    if os.path.exists(LOGO_PATH):
        await message.reply_photo(photo=LOGO_PATH, caption=caption, reply_markup=start_panel(client.me.username))
    else:
        await message.reply_text(text=caption, reply_markup=start_panel(client.me.username))

@Client.on_callback_query()
async def centralized_callbacks(client, query):
    data = query.data
    chat_id = query.message.chat.id

    if data == "start_menu":
        await query.message.edit_caption(caption="🏠 Ana Menüye Dönüldü.", reply_markup=start_panel(client.me.username))

    elif data == "help_main":
        await query.message.edit_caption(caption="🛠️ **Yardım Kategorileri**\n\nLütfen bilgi almak istediğiniz kategoriyi seçin:", reply_markup=help_main_markup())

    elif data == "help_music":
        await query.message.edit_caption(
            caption="🎵 **Müzik Komutları**\n\n• `/play` : Şarkı başlatır.\n• `/skip` : Şarkıyı atlar.\n• `/dur` : Yayını durdurur.\n• `/devam` : Yayını sürdürür.\n• `/bitir` : Yayını kapatır.\n• `/que` : Kuyruğu listeler.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="help_main")]])
        )

    elif data == "help_tag":
        await query.message.edit_caption(
            caption="🏷️ **Etiketleme Komutları**\n\n• `/tag` : Üyeleri etiketler.\n• `/gtag` : Günaydın mesajı.\n• `/itag` : İyi geceler mesajı.\n• `/stag` : Sohbete çağırma.\n• `/ktag` : Kurt oyunu çağrısı.\n• `/cancel` : İşlemi durdurur.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="help_main")]])
        )

    elif data == "skip":
        from assistant import on_stream_end_handler
        await query.message.delete()
        await on_stream_end_handler(client, type('obj', (object,), {'chat_id': chat_id}))

    elif data == "end":
        player.music_queue.pop(chat_id, None)
        try: await player.call.leave_group_call(chat_id)
        except: pass
        await query.message.delete()
