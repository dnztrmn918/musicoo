from pyrogram import Client, filters
import config
from database import add_sudo_user, remove_sudo_user, get_sudo_users, is_sudo

# ────────────────────────────────────────────────
#  SADECE OWNER YETKİLİ KOMUTLAR
# ────────────────────────────────────────────────
@Client.on_message(filters.command("sudoadd"))
async def sudo_add(client, message):
    uid = message.from_user.id
    if uid != config.SUDO_OWNER_ID:
        return await message.reply("⛔ **Bu yetki sadece bot sahibine aittir.**")

    target = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else (int(message.command[1]) if len(message.command) > 1 else None)
    )

    if not target:
        return await message.reply("📎 Kullanıcı ID belirtin veya bir mesaja yanıtlayın.")
    if target == config.SUDO_OWNER_ID:
        return await message.reply("⚠️ Sahibin zaten sudo yetkisi var.")

    await add_sudo_user(target)
    await message.reply(f"✅ `{target}` **sudo listesine eklendi.**")


@Client.on_message(filters.command("sudosil"))
async def sudo_del(client, message):
    uid = message.from_user.id
    if uid != config.SUDO_OWNER_ID:
        return await message.reply("⛔ **Bu yetki sadece bot sahibine aittir.**")

    target = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else (int(message.command[1]) if len(message.command) > 1 else None)
    )
    if not target:
        return await message.reply("📎 Kullanıcı ID belirtin veya bir mesaja yanıtlayın.")
    if target == config.SUDO_OWNER_ID:
        return await message.reply("⚠️ Owner silinemez.")

    await remove_sudo_user(target)
    await message.reply(f"🗑 `{target}` **sudo listesinden çıkarıldı.**")


# ────────────────────────────────────────────────
#  SUDO LİSTE KOMUTU
# ────────────────────────────────────────────────
@Client.on_message(filters.command("sudolist"))
async def sudo_list(client, message):
    if not await is_sudo(message.from_user.id):
        return
    sudos = await get_sudo_users()
    text = "👑 **Sudo Kullanıcıları**\n\n"
    for i, uid in enumerate(sudos, start=1):
        text += f"`{i}.` `{uid}`\n"
    await message.reply(text)
