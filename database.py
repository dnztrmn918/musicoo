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

# --- KULLANICI / GRUP EKLEME ---
async def add_served_user(user_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO served_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)

async def add_served_chat(chat_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO served_chats (chat_id) VALUES ($1) ON CONFLICT DO NOTHING", chat_id)

# --- SUDO (YÖNETİCİ) İŞLEMLERİ ---
async def add_sudo_user(user_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO sudo_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)

async def remove_sudo_user(user_id):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM sudo_users WHERE user_id = $1", user_id)

# --- VERİ ÇEKME FONKSİYONLARI ---
async def get_served_users(): return []
async def get_served_chats(): return []
async def get_sudo_users(): return []
async def is_sudo(u): return u == config.SUDO_OWNER_ID
