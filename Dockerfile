FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg git gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Önbelleği YOK SAYIP paketleri zorla en baştan kurmasını söylüyoruz:
RUN pip install --no-cache-dir --upgrade pip --ignore-installed
RUN pip install --no-cache-dir -r requirements.txt --ignore-installed

COPY . .

CMD ["python", "main.py"]
