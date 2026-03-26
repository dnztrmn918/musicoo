FROM python:3.9-slim

# curl aracı ile Node.js 18 sürümünü indirip kuruyoruz (FFmpeg ve diğerleriyle birlikte)
RUN apt-get update && apt-get install -y curl ffmpeg git gcc python3-dev && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip --ignore-installed
RUN pip install --no-cache-dir -r requirements.txt --ignore-installed

COPY . .

CMD ["python", "main.py"]
