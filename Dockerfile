FROM python:3.10-slim

WORKDIR /app

# Sadece gerekli sistem bağımlılıkları ve FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    libopus-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Bağımlılıkları temiz bir şekilde kur
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Çakışmaları önlemek için (Opsiyonel ama garantidir)
RUN pip uninstall -y pyrofork pyrogram && pip install pyrogram py-tgcalls==2.2.11

CMD ["python3", "main.py"]
