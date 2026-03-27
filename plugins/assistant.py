import asyncio
import player
from pyrogram.errors import UserAlreadyParticipant, FloodWait, ChatAdminRequired

async def assistant_join(client, chat_id):
    """Asistanın grupta olup olmadığını kontrol eder, yoksa katılır."""
    from main import userbot
    try:
        me = await userbot.get_me()
        await client.get_chat_member(chat_id, me.id)
        return True
    except:
        try:
            # Davet linki oluştur ve katıl
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
        except Exception:
            return False
