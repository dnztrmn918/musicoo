import asyncpg
import config
import asyncio

db_pool = None

async def init_db():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(config.DATABASE_URL)
    print("✅ PostgreSQL veritabanı hazır!")

async def get_db():
    global db_pool
    if db_pool is None: await init_db()
    return db_pool

async def add_served_user(user_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO served_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)

async def add_served_chat(chat_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO served_chats (chat_id) VALUES ($1) ON CONFLICT DO NOTHING", chat_id)

async def add_sudo_user(user_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO sudo_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)

async def remove_sudo_user(user_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM sudo_users WHERE user_id = $1", user_id)

# --- BOŞ OLAN VERİ ÇEKME FONKSİYONLARI DOLDURULDU ---
async def get_served_users():
    pool = await get_db()
    async with pool.acquire() as conn:
        records = await conn.fetch("SELECT user_id FROM served_users")
        return [r["user_id"] for r in records]

async def get_served_chats():
    pool = await get_db()
    async with pool.acquire() as conn:
        records = await conn.fetch("SELECT chat_id FROM served_chats")
        return [r["chat_id"] for r in records]

async def get_sudo_users():
    pool = await get_db()
    async with pool.acquire() as conn:
        records = await conn.fetch("SELECT user_id FROM sudo_users")
        return [r["user_id"] for r in records]

async def is_sudo(user_id):
    if user_id == config.SUDO_OWNER_ID:
        return True
    sudos = await get_sudo_users()
    return user_id in sudos
