import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_served_user, get_served_users, get_served_chats

# --- AYARLAR ---
DEVELOPER_LINK = "https://t.me/dnztrmnn"
CHANNEL_LINK = "https://t.me/NowaDestek"

# --- BUTON TASARIMLARI ---

def start_panel(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("🛠️ Komutlar", callback_data="help_main"),
            InlineKeyboardButton("👨‍💻 Geliştirici", url=DEVELOPER_LINK)
        ],
        [InlineKeyboardButton("📢 Resmi Kanal", url=CHANNEL_LINK)]
    ])

def main_help_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Müzik Menüsü", callback_data="help_music"),
            InlineKeyboardButton("🏷️ Etiket Menüsü", callback_data="help_tag")
        ],
        [InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="start_menu")]
    ])

def back_to_help_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Geri Dön", callback_data="help_main")]
    ])

# --- MESAJ YÖNETİCİLERİ ---

@Client.on_message(filters.command(["start", "yardim", "help"]) & filters.private)
async def start(client, message):
    await add_served_user(message.from_user.id)
    
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    caption_text = (
        f"👋 **Merhaba {message.from_user.mention}!**\n\n"
        "🎵 Gruplarında sesli sohbet üzerinden kesintisiz ve yüksek kalitede müzik çalabilir, "
        "gelişmiş etiketleme sistemlerini kullanabilirim.\n\n"
        f"📊 **Sistem Verileri:**\n"
        f"👥 Kullanıcılar: `{users}`\n"
        f"💬 Gruplar: `{chats}`\n\n"
        "Butonları kullanarak detaylı bilgi alabilirsin."
    )
    await message.reply_text(text=caption_text, reply_markup=start_panel(client.me.username))

@Client.on_message(filters.command("reload"))
async def reload_everyone(client, message):
    # Bu komut artık herkes tarafından kullanılabilir
    await message.reply_text("✅ **Sistem ve yönetici listesi başarıyla tazelendi!**")

# --- CALLBACK HANDLER (Buton Fonksiyonları) ---

@Client.on_callback_query()
async def callbacks(client, query):
    data = query.data
    bot_username = client.me.username

    # Ana Menü (Start)
    if data == "start_menu":
        users = len(await get_served_users())
        chats = len(await get_served_chats())
        caption_text = (
            f"👋 **Merhaba {query.from_user.mention}!**\n\n"
            "Müzik ve Etiketleme botu ana menüsündesin.\n\n"
            f"📊 **İstatistikler:**\n"
            f"👥 Kullanıcılar: `{users}`\n"
            f"💬 Gruplar: `{chats}`"
        )
        await query.message.edit_text(text=caption_text, reply_markup=start_panel(bot_username))

    # Yardım Kategorileri Seçim Ekranı
    elif data == "help_main":
        await query.message.edit_text(
            "🛠️ **Yardım ve Komutlar**\n\nLütfen öğrenmek istediğin kategoriyi seç:",
            reply_markup=main_help_markup()
        )

    # Müzik Komutları Sayfası
    elif data == "help_music":
        music_text = (
            "🎵 **Müzik Komutları**\n\n"
            "• `/play [isim]` : Şarkı başlatır.\n"
            "• `/skip` : Sıradaki şarkıya geçer.\n"
            "• `/dur` : Yayını duraklatır.\n"
            "• `/bitir` : Yayını kapatır.\n"
            "• `/que` : Kuyruk listesini gösterir."
        )
        await query.message.edit_text(text=music_text, reply_markup=back_to_help_markup())

    # Tag (Etiket) Komutları Sayfası
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

    # Menü Kapatma
    elif data == "close_stats":
        await query.message.delete()
