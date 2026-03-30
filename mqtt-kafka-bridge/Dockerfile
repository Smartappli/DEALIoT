FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    kafka-python \
    lz4 \
    paho-mqtt

RUN useradd --create-home --shell /bin/bash appuser
COPY bridge.py /app/bridge.py
RUN chown appuser:appuser /app/bridge.py

USER appuser
CMD ["python", "-u", "/app/bridge.py"]
