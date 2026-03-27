import os

# ──────────────────────────────
# TEMEL BOT AYARLARI
# ──────────────────────────────
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION = os.getenv("SESSION", "")

# ──────────────────────────────
# VERİTABANI AYARLARI
# ──────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")  # Koyeb Postgres URL'i

# ──────────────────────────────
# LOG / STATISTICS AYARLARI
# ──────────────────────────────
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1002222222222"))
STATS_CHANNEL_ID = int(os.getenv("STATS_CHANNEL_ID", "-1003333333333"))

# ──────────────────────────────
# SUDO VE OWNER TANIMLARI
# ──────────────────────────────
# BOT OWNER ⇒ yalnız bu kullanıcı diğer sudo’ları ekleyip / silebilir
SUDO_OWNER_ID = int(os.getenv("SUDO_OWNER_ID", "0"))

# opsiyonel başlangıç sudo listesi (OWNER daima eklenir)
SUDO_USERS = [
    int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip().isdigit()
]
if SUDO_OWNER_ID and SUDO_OWNER_ID not in SUDO_USERS:
    SUDO_USERS.append(SUDO_OWNER_ID)

# ──────────────────────────────
# DİĞER AYARLAR
# ──────────────────────────────
DEVELOPER_LINK = "[t.me](https://t.me/dnztrmnn)"
CHANNEL_LINK = "[t.me](https://t.me/NowaDestek)"
LOGO_PATH = os.path.join(os.getcwd(), "plugins", "logo.jpg")
