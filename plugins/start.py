import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    # Logoyu 'plugins' klasörünün içinde arar
    logo_path = "./plugins/logo.jpg" 
    
    caption_text = (
        "👋 **Merhaba! Ben Pi-Müzik Botu.**\n\n"
        "🎵 Gruplarında sesli sohbet üzerinden yüksek kalitede müzik çalabilirim.\n\n"
        "🚀 **Hemen başlamak için:**\n"
        "1️⃣ Beni bir gruba ekle.\n"
        "2️⃣ Grupta yönetici yap.\n"
        "3️⃣ `/play şarkı adı` komutunu kullan."
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{client.me.username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton("🛠️ Yardım & Komutlar", callback_data="help_menu"),
        ]
    ])

    if os.path.exists(logo_path):
        await message.reply_photo(
            photo=logo_path,
            caption=caption_text,
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            text=caption_text,
            reply_markup=buttons
        )
