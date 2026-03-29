import asyncpg
import config
import asyncio

db_pool = None

# ──────────────────────────────
#  BAĞLANTI VE TABLO OLUŞTURMA
# ──────────────────────────────
async def init_db():
    global db_pool
    try:
        # Eğer zaten bağlıysa tekrar deneme
        if db_pool:
            return db_pool
            
        # Bağlantı havuzunu oluştur (5 saniye zaman aşımı ekledik bot donmasın diye)
        db_pool = await asyncio.wait_for(asyncpg.create_pool(config.DATABASE_URL), timeout=5.0)
        
        async with db_pool.acquire() as conn:
            await conn.execute("CREATE TABLE IF NOT EXISTS served_users (user_id BIGINT PRIMARY KEY)")
            await conn.execute("CREATE TABLE IF NOT EXISTS served_chats (chat_id BIGINT PRIMARY KEY)")
            await conn.execute("CREATE TABLE IF NOT EXISTS sudo_users (user_id BIGINT PRIMARY KEY)")
        
        print("✅ PostgreSQL veritabanı hazır!")
        return db_pool
    except Exception as e:
        print(f"❌ Veritabanı Hatası: {e}")
        db_pool = None
        return None

# Bağlantı havuzunu güvenli bir şekilde kontrol eden yardımcı fonksiyon
async def get_db():
    global db_pool
    if db_pool is None:
        return await init_db()
    return db_pool

# ──────────────────────────────
#  KULLANICI / GRUP YÖNETİMİ
# ──────────────────────────────
async def add_served_user(user_id: int):
    # Arka planda çalıştırarak botun mesaj hızını ve müziği etkilemesini engelleriz
    asyncio.create_task(_add_served_user_logic(user_id))

async def _add_served_user_logic(user_id: int):
    pool = await get_db()
    if not pool: return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO served_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id
            )
    except: pass

async def get_served_users():
    pool = await get_db()
    if not pool: return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM served_users")
            return [r["user_id"] for r in rows]
    except: return []

async def add_served_chat(chat_id: int):
    pool = await get_db()
    if not pool: return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO served_chats (chat_id) VALUES ($1) ON CONFLICT DO NOTHING", chat_id
            )
    except: pass

async def get_served_chats():
    pool = await get_db()
    if not pool: return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT chat_id FROM served_chats")
            return [r["chat_id"] for r in rows]
    except: return []

# ──────────────────────────────
#  SUDO KULLANICI YÖNETİMİ
# ──────────────────────────────
async def add_sudo_user(user_id: int):
    pool = await get_db()
    if not pool: return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO sudo_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id
            )
    except: pass

async def remove_sudo_user(user_id: int):
    pool = await get_db()
    if not pool: return
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM sudo_users WHERE user_id=$1", user_id)
    except: pass

async def get_sudo_users():
    pool = await get_db()
    if not pool: return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM sudo_users")
            return [r["user_id"] for r in rows]
    except: return []

async def is_sudo(user_id: int) -> bool:
    if user_id == config.SUDO_OWNER_ID:
        return True
    pool = await get_db()
    if not pool: return False
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 FROM sudo_users WHERE user_id=$1", user_id)
        return bool(row)
    except: return False
