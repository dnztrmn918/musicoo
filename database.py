import asyncpg
import config

db_pool = None


# ──────────────────────────────
#  BAĞLANTI VE TABLO OLUŞTURMA
# ──────────────────────────────
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(config.DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS served_users (user_id BIGINT PRIMARY KEY)")
        await conn.execute("CREATE TABLE IF NOT EXISTS served_chats (chat_id BIGINT PRIMARY KEY)")
        await conn.execute("CREATE TABLE IF NOT EXISTS sudo_users (user_id BIGINT PRIMARY KEY)")
    print("✅ PostgreSQL veritabanı hazır!")


# ──────────────────────────────
#  KULLANICI / GRUP YÖNETİMİ
# ──────────────────────────────
async def add_served_user(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO served_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id
        )


async def get_served_users():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM served_users")
        return [r["user_id"] for r in rows]


async def add_served_chat(chat_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO served_chats (chat_id) VALUES ($1) ON CONFLICT DO NOTHING", chat_id
        )


async def get_served_chats():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT chat_id FROM served_chats")
        return [r["chat_id"] for r in rows]


# ──────────────────────────────
#  SUDO KULLANICI YÖNETİMİ
# ──────────────────────────────
async def add_sudo_user(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO sudo_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id
        )


async def remove_sudo_user(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM sudo_users WHERE user_id=$1", user_id)


async def get_sudo_users():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM sudo_users")
        return [r["user_id"] for r in rows]


async def is_sudo(user_id: int) -> bool:
    if user_id == config.SUDO_OWNER_ID:
        return True
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM sudo_users WHERE user_id=$1", user_id)
    return bool(row)
