# Python 3.10 (En kararlı sürüm) kullanıyoruz
FROM python:3.10-slim-buster

# Sistem için gerekli araçları ve FFmpeg'i kuruyoruz
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Dosyaları kopyala
COPY . .

# Kütüphaneleri kur
RUN pip install --no-cache-dir -r requirements.txt

# Botu çalıştır
CMD ["python", "main.py"]
