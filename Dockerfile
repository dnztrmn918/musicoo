FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg git build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Dosyaları kopyalama komutunu düzelttik (Eski kodda hata vardı)
COPY . /app

# --- KOYEB'İ ZORLA SIFIRLAMA KODU ---
# Bu satır değiştiği için Koyeb tüm önbelleği çöpe atacak
ENV CACHE_BUSTER="PiMuzik_V2_Kesin_Cozum"

RUN pip install --upgrade pip

# Eski hatalı kütüphaneleri zorla siliyoruz
RUN pip uninstall -y pyrogram pyrofork py-tgcalls tgcrypto yt-dlp asyncpg

# requirements.txt'yi temiz kurulumla indiriyoruz
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
