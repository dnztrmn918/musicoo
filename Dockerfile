# Python 3.11-slim kullanımı bu kütüphaneler için en kararlı yoldur
FROM python:3.11-slim

# Gerekli sistem paketlerini kuruyoruz
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    gcc \
    git \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları kopyala
COPY . . [cite: 2, 3]

CMD ["python", "main.py"]
