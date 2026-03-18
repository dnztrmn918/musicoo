# Daha güncel ve sorunsuz olan Bullseye sürümüne geçtik
FROM python:3.10-slim-bullseye

# Sistem paketlerini kuruyoruz
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Dosyaları kopyala
COPY . .

# Kütüphaneleri kur
RUN pip install --no-cache-dir -r requirements.txt

# Botu çalıştır
CMD ["python", "main.py"]
