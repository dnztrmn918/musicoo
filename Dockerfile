# Kararlı ve hafif bir Python 3.10 sürümü kullanıyoruz
FROM python:3.10-slim

# FFmpeg ve kütüphane derlemeleri için gereken temel sistem araçlarını kuruyoruz
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# Gereksinim dosyasını kopyalayıp kütüphaneleri kuruyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Projedeki tüm dosyaları kopyalıyoruz
COPY . .

# Botu başlatma komutu
CMD ["python", "main.py"]
