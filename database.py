import asyncpg
import config

db_pool = None

async def init_db():
    global db_pool
    if not config.DATABASE_URL:
        return
    db_pool = await asyncpg.create_pool(config.DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS served_users (user_id BIGINT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS served_chats (chat_id BIGINT PRIMARY KEY);
        ''')
    print("✅ PostgreSQL Veritabanı Hazır!")

async def add_served_user(user_id: int):
    if db_pool:
        async with db_pool.acquire() as conn:
            await conn.execute('INSERT INTO served_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING', user_id)

async def get_served_users():
    if db_pool:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch('SELECT user_id FROM served_users')
            return [row['user_id'] for row in rows]
    return []

async def add_served_chat(chat_id: int):
    if db_pool:
        async with db_pool.acquire() as conn:
            await conn.execute('INSERT INTO served_chats (chat_id) VALUES ($1) ON CONFLICT DO NOTHING', chat_id)

async def get_served_chats():
    if db_pool:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch('SELECT chat_id FROM served_chats')
            return [row['chat_id'] for row in rows]
    return []
