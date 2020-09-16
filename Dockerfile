FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt update && apt upgrade -y && pip install --no-cache-dir -r requirements.txt

COPY ./bot.py .
COPY ./bin ./bin
COPY ./fonts ./fonts

VOLUME [ "/data", "/logs", "/config" ]

CMD ["python", "./bot.py"]