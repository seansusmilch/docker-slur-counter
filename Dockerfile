FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt update && apt upgrade && pip install --no-cache-dir -r requirements.txt

COPY ./bot.py .

VOLUME [ "/data/users", "/data/words", "/logs", "/config" ]

# RUN mkdir /data/users /data/words

CMD ["python", "./bot.py"]