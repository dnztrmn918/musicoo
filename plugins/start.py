from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_user, get_served_users, get_served_chats

DEVELOPER_LINK = "https://t.me/SeninKullaniciAdin"
CHANNEL_LINK = "https://t.me/Kanalin"

def start_panel(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("🛠️ Yardım", callback_data="help_menu"),
            InlineKeyboardButton("👨‍💻 Geliştirici", url=DEVELOPER_LINK)
        ],
        [InlineKeyboardButton("📢 Resmi Kanal", url=CHANNEL_LINK)]
    ])

def help_panel():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="start_menu")]])

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await add_served_user(message.from_user.id)
    
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    caption_text = (
        f"👋 **Merhaba {message.from_user.mention}! Ben Pi-Müzik Botu.**\n\n"
        "🎵 Gruplarında sesli sohbet üzerinden kesintisiz ve yüksek kalitede müzik çalabilirim.\n\n"
        f"📊 **Aktif İstatistikler:**\n"
        f"👥 Kullanıcılar: `{users}`\n"
        f"💬 Gruplar: `{chats}`\n\n"
        "Aşağıdaki butonları kullanarak beni grubuna ekleyebilir veya komutlarımı öğrenebilirsin."
    )
    await message.reply_text(text=caption_text, reply_markup=start_panel(client.me.username))

@Client.on_callback_query(filters.regex("help_menu"))
async def help_menu(client, CallbackQuery):
    help_text = (
        "🛠️ **Pi-Müzik Kullanım Kılavuzu**\n\n"
        "▶️ `/play` veya `/oynat` - Şarkı çalar/sıraya ekler.\n"
        "⏸ `/stop` veya `/dur` - O anki şarkıyı duraklatır.\n"
        "⏹ `/end` veya `/bitir` - Müziği kapatır ve botu odadan çıkarır.\n"
        "📋 `/que` veya `/list` - (Sadece Sudo) Kuyruk listesini gösterir.\n\n"
        "💡 **Önemli:** Botun çalışması için grupta yönetici olması ve Sesli Sohbetin başlatılmış olması gerekir."
    )
    await CallbackQuery.message.edit_text(text=help_text, reply_markup=help_panel())

@Client.on_callback_query(filters.regex("start_menu"))
async def start_menu(client, CallbackQuery):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    caption_text = (
        f"👋 **Merhaba {CallbackQuery.from_user.mention}! Ben Pi-Müzik Botu.**\n\n"
        "🎵 Gruplarında sesli sohbet üzerinden kesintisiz ve yüksek kalitede müzik çalabilirim.\n\n"
        f"📊 **Aktif İstatistikler:**\n"
        f"👥 Kullanıcılar: `{users}`\n"
        f"💬 Gruplar: `{chats}`\n\n"
        "Aşağıdaki butonları kullanarak beni grubuna ekleyebilir veya komutlarımı öğrenebilirsin."
    )
    await CallbackQuery.message.edit_text(text=caption_text, reply_markup=start_panel(client.me.username))
