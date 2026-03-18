# Python 3.13 slim sürümü hem hafif hem de en güncel özelliklere sahiptir
FROM python:3.13-slim

# Sistem güncellemeleri ve müzik botu için gerekli bağımlılıklar
# ffmpeg: Ses işleme için ŞART
# build-essential & gcc: Bazı Python paketlerinin derlenmesi için gerekli
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Önce sadece requirements kopyalanır (Docker cache avantajı için)
COPY requirements.txt .

# Bağımlılıkları kur
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Projedeki tüm dosyaları kopyala
COPY . .

# Botu çalıştır
CMD ["python", "main.py"]
