import asyncio
import player
from pyrogram.errors import UserAlreadyParticipant, FloodWait, ChatAdminRequired

async def assistant_join(client, chat_id):
    """Asistanın grupta olup olmadığını kontrol eder, yoksa katılır."""
    userbot = player.userbot  
    
    # GÜVENLİK KONTROLÜ: Eğer userbot bağlanmamışsa, başlat!
    if not userbot.is_connected:
        try:
            await userbot.start()
            await asyncio.sleep(2) # Sisteme oturması için bekle
        except Exception as e:
            return f"Asistan başlatılamadı: {e}"

    try:
        # Önce asistanın grupta olup olmadığını kendi gözüyle kontrol ediyoruz
        me = await userbot.get_me()
        await client.get_chat_member(chat_id, me.id)
        return True
    except Exception as e1:
        try:
            # Grupta değilse veya göremiyorsa link ile katılmaya çalışır
            invitelink = await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(invitelink)
            return True
        except UserAlreadyParticipant:
            return True
        except ChatAdminRequired:
            return "ADMIN_REQUIRED"
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await assistant_join(client, chat_id)
        except Exception as e2:
            return f"JOIN_ERROR: {str(e2)} (Grup İçi Kontrol: {str(e1)})"
