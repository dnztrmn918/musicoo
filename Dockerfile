FROM python:3.10-slim

WORKDIR /app

# Node.js, FFmpeg ve Deno (YouTube JS şifrelemesi için zorunlu)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && curl -fsSL https://deno.land/x/install/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Deno yolunu sisteme ekliyoruz
ENV PATH="/root/.deno/bin:$PATH"

COPY . .

# Python bağımlılıklarını yüklüyoruz
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]

# V2 MOTORUNA GECIS ICIN ONBELLEK TEMIZLIGI
