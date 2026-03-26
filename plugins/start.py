from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    bot_info = await client.get_me()
    
    welcome_text = (
        "🎵 **Pi-Müzik Botuna Hoş Geldiniz!**\n\n"
        "Telegram gruplarınızda kesintisiz ve yüksek kaliteli müzik dinlemenizi sağlayan "
        "gelişmiş bir altyapıya sahibim. Şarkıları aramak, oynatmak ve yönetmek için tasarlandım.\n\n"
        "Hemen beni grubunuza ekleyerek müziğin tadını çıkarın!"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{bot_info.username}?startgroup=true")],
        [
            InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/GelistiriciKullaniciAdin"),
            InlineKeyboardButton("❓ Yardım", callback_data="help_menu")
        ],
        [InlineKeyboardButton("📢 Resmi Kanal", url="https://t.me/KanalKullaniciAdin")]
    ])
    
    await message.reply_text(
        text=welcome_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
