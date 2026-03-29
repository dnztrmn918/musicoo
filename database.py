import asyncpg
import config
import asyncio

db_pool = None

async def init_db():
    global db_pool
    try:
        if db_pool is None:
            db_pool = await asyncio.wait_for(asyncpg.create_pool(config.DATABASE_URL), timeout=10.0)
            async with db_pool.acquire() as conn:
                await conn.execute("CREATE TABLE IF NOT EXISTS served_users (user_id BIGINT PRIMARY KEY)")
                await conn.execute("CREATE TABLE IF NOT EXISTS served_chats (chat_id BIGINT PRIMARY KEY)")
                await conn.execute("CREATE TABLE IF NOT EXISTS sudo_users (user_id BIGINT PRIMARY KEY)")
            print("✅ PostgreSQL veritabanı hazır!")
    except Exception as e:
        print(f"❌ Veritabanı başlatılamadı: {e}")

async def get_db():
    global db_pool
    if db_pool is None:
        await init_db()
    return db_pool

async def add_served_user(user_id: int):
    pool = await get_db()
    if not pool: return
    try:
        async with pool.acquire() as conn:
            await conn.execute("INSERT INTO served_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
    except Exception as e:
        print(f"DB Hatası: {e}")

async def get_served_users():
    pool = await get_db()
    if not pool: return []
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM served_users")
        return [r["user_id"] for r in rows]

# Gerekli diğer boş fonksiyonlar (Hata vermemesi için)
async def get_served_chats(): return []
async def is_sudo(u): return u == config.SUDO_OWNER_ID
