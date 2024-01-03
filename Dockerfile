FROM python:3.12
RUN apt-get update \
 && apt-get install -y firefox-esr \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
RUN chmod 755 .
COPY . .