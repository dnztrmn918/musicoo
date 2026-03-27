import asyncio
import player
from pyrogram.errors import UserAlreadyParticipant, FloodWait, ChatAdminRequired

async def assistant_join(client, chat_id):
    """Asistanın grupta olup olmadığını kontrol eder, yoksa katılır."""
    userbot = player.userbot  # Döngüsel hatayı kökten çözen satır
    try:
        me = await userbot.get_me()
        await client.get_chat_member(chat_id, me.id)
        return True
    except:
        try:
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
