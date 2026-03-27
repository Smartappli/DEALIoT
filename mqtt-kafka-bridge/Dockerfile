FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    paho-mqtt \
    kafka-python \
    orjson \
    lz4

COPY bridge.py /app/bridge.py

CMD ["python", "-u", "/app/bridge.py"]
