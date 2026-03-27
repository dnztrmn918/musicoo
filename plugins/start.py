import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_user, get_served_users, get_served_chats
import player, config

LOGO_PATH = os.path.join(os.getcwd(), "plugins", "logo.jpg")

def start_panel(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("🛠️ Komutlar", callback_data="help_main"), 
         InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/dnztrmnn")],
        [InlineKeyboardButton("📢 Resmi Kanal", url="https://t.me/NowaDestek")]
    ])

def help_main_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Müzik", callback_data="help_music"),
         InlineKeyboardButton("🏷️ Etiket", callback_data="help_tag")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="start_menu")]
    ])

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await add_served_user(message.from_user.id)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    caption = f"👋 **Merhaba {message.from_user.mention}!**\n\n📊 Kullanıcı: `{users}` | Grup: `{chats}`"
    
    if os.path.exists(LOGO_PATH):
        await message.reply_photo(photo=LOGO_PATH, caption=caption, reply_markup=start_panel(client.me.username))
    else:
        await message.reply_text(text=caption, reply_markup=start_panel(client.me.username))

@Client.on_callback_query()
async def callbacks(client, query):
    data = query.data
    chat_id = query.message.chat.id

    if data == "start_menu":
        await query.message.edit_caption(caption="Ana Menüye Dönüldü.", reply_markup=start_panel(client.me.username))
    elif data == "help_main":
        await query.message.edit_caption(caption="Yardım kategorisini seçin:", reply_markup=help_main_markup())
    elif data == "help_music":
        await query.message.edit_caption(caption="🎵 **Müzik Komutları**\n• `/play` , `/skip` , `/dur` , `/bitir`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="help_main")]]))
    elif data == "help_tag":
        await query.message.edit_caption(caption="🏷️ **Etiketleme**\n• `/tag` , `/gtag` , `/itag` , `/cancel`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="help_main")]]))
    elif data == "skip":
        from assistant import on_stream_end_handler
        await query.message.delete()
        await on_stream_end_handler(client, type('obj', (object,), {'chat_id': chat_id}))
    elif data == "end":
        player.music_queue.pop(chat_id, None)
        try: await player.call.leave_group_call(chat_id)
        except: pass
        await query.message.delete()
