FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Europe/Moscow

# update apk repo and TZ
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
 && echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \
 && apk update \
 && apk add --no-cache \
    gcc musl-dev libffi-dev openssl-dev build-base firefox tzdata \
 && pip install --no-cache-dir --upgrade pip \
 && cp /usr/share/zoneinfo/$TZ /etc/localtime \
 && apk del tzdata

WORKDIR /app

# install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . .
