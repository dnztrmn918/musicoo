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

async def add_sudo_user(user_id): # HATA BURADAYDI, EKLEDİK
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO sudo_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)

async def get_served_users(): return []
async def get_served_chats(): return []
async def get_sudo_users(): return []
