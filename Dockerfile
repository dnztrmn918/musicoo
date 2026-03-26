# Python 3.10-slim kullanarak hem boyutu küçültüyoruz hem de 3.9 uyarısını kaldırıyoruz
FROM python:3.10-slim

# Çalışma dizinini belirliyoruz
WORKDIR /app

# Sistem bağımlılıklarını yüklüyoruz (FFmpeg ses işleme için mecburidir)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Tüm dosyaları konteynere kopyalıyoruz
COPY . .

# Python kütüphanelerini yüklüyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Botu başlatan komut
CMD ["python3", "main.py"]
