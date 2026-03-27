from motor.motor_asyncio import AsyncIOMotorClient
import config

if config.MONGO_DB_URI:
    client = AsyncIOMotorClient(config.MONGO_DB_URI)
    db = client.pimusic
    usersdb = db.users
    chatsdb = db.chats
else:
    usersdb = None
    chatsdb = None

async def add_served_user(user_id: int):
    if usersdb is not None:
        if not await usersdb.find_one({"user_id": user_id}):
            await usersdb.insert_one({"user_id": user_id})

async def get_served_users():
    return await usersdb.to_list(length=None) if usersdb is not None else []

async def add_served_chat(chat_id: int):
    if chatsdb is not None:
        if not await chatsdb.find_one({"chat_id": chat_id}):
            await chatsdb.insert_one({"chat_id": chat_id})

async def get_served_chats():
    return await chatsdb.to_list(length=None) if chatsdb is not None else []
