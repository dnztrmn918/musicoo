# Python 3.10 sürümünü Bullseye altyapısıyla kullanıyoruz (En kararlı sürüm)
FROM python:3.10-slim-bullseye

# Sistem güncellemelerini yap ve müzik botu için ŞART olan paketleri kur
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    libsndio-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini /app olarak ayarla
WORKDIR /app

# Projedeki tüm dosyaları konteyner içine kopyala
COPY . .

# Pip'i güncelle ve kütüphane çakışmalarını aşmak için legacy-resolver kullan
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

# Botu çalıştıracak ana komut
CMD ["python", "main.py"]
