# Orijinal dosyandaki Python 3.9 yerine, hata almamak için 3.10-slim kullanıyoruz
FROM python:3.10-slim

# Çalışma dizini senin dosyandaki gibi /app
WORKDIR /app

# Koyeb ve Sesli Sohbet için gerekli sistem araçları (FFmpeg ve Git)
# Senin orijinal dosyandaki kurulum mantığını koruyarak güncelledim
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Tüm dosyaları kopyalıyoruz
COPY . .

# Gereksinimleri yüklüyoruz (requirements.txt içindekiler)
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Botu başlatan komut (Senin main.py dosyanı çalıştırır)
CMD ["python3", "main.py"]
