FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg git build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# KOYEB'İ YENİDEN İNDİRMEYE ZORLAYAN KOD
ENV CACHE_BUSTER="MODERN_V2_STACK_01"

RUN pip install --upgrade pip

# Eski ne varsa zorla söküp atıyoruz
RUN pip uninstall -y pyrogram pyrofork py-tgcalls tgcrypto yt-dlp asyncpg

# Tertemiz, güncel kurulum
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
