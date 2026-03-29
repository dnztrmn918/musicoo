FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg git build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# ESKİ VE HATALI NE VARSA ZORLA SİLİYORUZ
RUN pip install --upgrade pip
RUN pip uninstall -y pyrogram pyrofork py-tgcalls
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
