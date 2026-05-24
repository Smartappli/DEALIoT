# syntax=docker/dockerfile:1.7

FROM python:3.13-slim

WORKDIR /app

COPY --chmod=0444 mqtt-kafka-bridge/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --only-binary :all: --require-hashes --requirement /tmp/requirements.txt \
 && useradd --create-home --shell /bin/bash appuser

COPY --chown=appuser:appuser --chmod=0444 mqtt-kafka-bridge/bridge.py /app/bridge.py
COPY --chown=appuser:appuser --chmod=0555 dealiot_contracts /app/dealiot_contracts

USER appuser
ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONPATH="/app"
CMD ["python", "-u", "/app/bridge.py"]
