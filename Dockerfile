FROM python:3.10-slim

WORKDIR /app

# Node.js, FFmpeg ve sistem araçlarını kuruyoruz
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Python bağımlılıklarını yüklüyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Botu başlat
CMD ["python3", "main.py"]
