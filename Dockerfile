FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt update && apt upgrade && pip install --no-cache-dir -r requirements.txt

COPY ./bot.py .
COPY ./bin ./bin

VOLUME [ "/data", "/logs", "/config" ]

CMD ["python", "./bot.py"]