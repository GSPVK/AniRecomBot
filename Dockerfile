FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# update apk repo
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
 && echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories 
RUN apk update

# timezone
RUN apk add -U tzdata
ENV TZ=Europe/Moscow
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime

# install packages
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev build-base firefox
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt
