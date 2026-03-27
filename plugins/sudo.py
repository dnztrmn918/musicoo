import time
from pyrogram import Client, filters
import config
from database import get_served_chats, get_served_users

@Client.on_message(filters.command("bilgi") & filters.user(config.SUDO_USERS))
async def info_to_channel(client, message):
    """
    Sadece Sudo kullanıcıları tarafından kullanılabilir.
    Botun hizmet verdiği grup ve kullanıcı sayılarını raporlar.
    """
    start_t = time.time()
    m = await message.reply_text("📊 **Güncel veriler toplanıyor...**")
    
    # Veritabanından (PostgreSQL) verileri çek
    try:
        all_chats = await get_served_chats()
        all_users = await get_served_users()
    except Exception as e:
        return await m.edit(f"❌ **Veritabanı hatası:** {e}")
    
    # Gecikme (Ping) hesapla
    ping = f"{round((time.time() - start_t) * 1000)} ms"
    
    # Rapor Taslağı
    stats_text = (
        "📢 **Pİ-MÜZİK SİSTEM RAPORU**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏠 **Toplam Grup:** `{len(all_chats)}` grup\n"
        f"👥 **Toplam Kullanıcı:** `{len(all_users)}` kişi\n"
        f"⚡️ **Sistem Gecikmesi:** `{ping}`\n"
        f"🛰 **Bağlantı Durumu:** `🟢 Aktif`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Sorgulayan:** {message.from_user.mention}\n"
        f"📅 **Tarih:** {time.strftime('%d/%m/%Y %H:%M:%S')}"
    )
    
    # 1. Mesajın altına Bilgi Kanalına gönderildiğine dair onay ver
    try:
        # İstatistikleri Kanala Gönder
        await client.send_message(config.STATS_CHANNEL_ID, stats_text)
        await m.edit("✅ **İstatistikler başarıyla Bilgi Kanalı'na iletildi!**")
    except Exception as e:
        await m.edit(f"⚠️ **Hata:** Veriler toplandı ancak kanala gönderilemedi.\n`Sebep: {e}`")

@Client.on_message(filters.command("duyuru") & filters.user(config.SUDO_USERS))
async def broadcast(client, message):
    """
    Sudo kullanıcıları için tüm gruplara mesaj gönderme taslağı.
    """
    if not message
