FROM python:3

WORKDIR /usr/src/app

COPY ./ ./
RUN apt update && apt upgrade -y && pip install --no-cache-dir -r requirements.txt

VOLUME ["/config", "/data"]

CMD ["python", "./prod.py"]