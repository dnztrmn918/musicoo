class Config:
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "") # Burayı da değişkene bağla
    STRING_SESSION = os.getenv("STRING_SESSION", "")
