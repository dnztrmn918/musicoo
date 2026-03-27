import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_user, get_served_users, get_served_chats
import player, config

# --- AYARLAR VE LOGO YOLU ---
DEVELOPER_LINK = "https://t.me/dnztrmnn"
CHANNEL_LINK = "https://t.me/NowaDestek"
# Logo dosyanın yolu (plugins klasörü içinde)
LOGO_PATH = os.path.join(os.getcwd(), "plugins", "logo.jpg")

# --- ŞIK PANEL TASARIMLARI ---

def start_panel(bot_username):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("🛠️ Komutlar", callback_data="help_main"),
            InlineKeyboardButton("👨‍💻 Geliştirici", url=DEVELOPER_LINK)
        ],
        [
            InlineKeyboardButton("📢 Resmi Kanal", url=CHANNEL_LINK)
        ]
    ])

def help_main_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Müzik Menüsü", callback_data="help_music"),
            InlineKeyboardButton("🏷️ Etiket Menüsü", callback_data="help_tag")
        ],
        [
            InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="start_menu")
        ]
    ])

# --- KOMUTLAR ---

@Client.on_message(filters.command(["start"]) & filters.private)
async def start(client, message):
    # Kullanıcıyı veritabanına ekle
    await add_served_user(message.from_user.id)
    
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    # Şık Karşılama Metni
    start_text = (
        f"✨ **Merhaba {message.from_user.mention}!**\n\n"
        f"🚀 **Nowa-Müzik Sistemine Hoş Geldin!**\n\n"
        f"🎶 Gruplarında sesli sohbet üzerinden kesintisiz, "
        f"yüksek kaliteli müzik deneyimi ve gelişmiş "
        f"etiketleme sistemleri için doğru yerdesin.\n\n"
        f"📊 **Güncel Sistem Verileri:**\n"
        f"┌ 👤 **Kullanıcılar:** `{users}`\n"
        f"└ 💬 **Aktif Gruplar:** `{chats}`\n\n"
        f"✨ *Müziğin ritmini bizimle yakala!*"
    )

    if os.path.exists(LOGO_PATH):
        await message.reply_photo(
            photo=LOGO_PATH,
            caption=start_text,
            reply_markup=start_panel(client.me.username)
        )
    else:
        await message.reply_text(
            text=start_text, 
            reply_markup=start_panel(client.me.username)
        )

# --- CALLBACK HANDLER (Buton Fonksiyonları) ---

@Client.on_callback_query()
async def centralized_callbacks(client, query):
    data = query.data
    chat_id = query.message.chat.id
    bot_username = client.me.username

    if data == "start_menu":
        users = len(await get_served_users())
        chats = len(await get_served_chats())
        start_text = (
            f"✨ **Nowa-Müzik Ana Menü**\n\n"
            f"📊 **Sistem Durumu:**\n"
            f"👤 Kullanıcı: `{users}`\n"
            f"💬 Grup: `{chats}`\n\n"
            f"Lütfen işlem yapmak için butonları kullanın."
        )
        try:
            await query.message.edit_caption(
                caption=start_text,
                reply_markup=start_panel(bot_username)
            )
        except:
            await query.message.edit_text(
                text=start_text,
                reply_markup=start_panel(bot_username)
            )

    elif data == "help_main":
        await query.message.edit_caption(
            caption="🛠️ **Yardım Paneli**\n\nÖğrenmek istediğiniz komut kategorisini seçin:",
            reply_markup=help_main_markup()
        )

    elif data == "help_music":
        music_text = (
            "🎵 **Müzik Komutları**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• `/play` ➪ Şarkı başlatır\n"
            "• `/skip` ➪ Şarkıyı atlar\n"
            "• `/dur` ➪ Yayını durdurur\n"
            "• `/devam` ➪ Yayını sürdürür\n"
            "• `/bitir` ➪ Yayını kapatır\n"
            "• `/que` ➪ Kuyruğu listeler\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await query.message.edit_caption(
            caption=music_text, 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="help_main")]])
        )

    elif data == "help_tag":
        tag_text = (
            "🏷️ **Etiket Komutları**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• `/tag` ➪ Klasik etiketleme\n"
            "• `/gtag` ➪ Günaydın mesajı\n"
            "• `/itag` : İyi geceler mesajı\n"
            "• `/stag` : Sohbete çağırma\n"
            "• `/ktag` : Kurt oyunu çağrısı\n"
            "• `/cancel` : İşlemi durdurur\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await query.message.edit_caption(
            caption=tag_text, 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="help_main")]])
        )

    elif data == "skip":
        from plugins.assistant import on_stream_end_handler
        await query.message.delete()
        await on_stream_end_handler(client, type('obj', (object,), {'chat_id': chat_id}))

    elif data == "end":
        player.music_queue.pop(chat_id, None)
        try: await player.call.leave_group_call(chat_id)
        except: pass
        await query.message.delete()
