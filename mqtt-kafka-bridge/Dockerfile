FROM python:3.13-slim

WORKDIR /app

COPY mqtt-kafka-bridge/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt

RUN useradd --create-home --shell /bin/bash appuser
COPY mqtt-kafka-bridge/bridge.py /app/bridge.py
COPY dealiot_contracts /app/dealiot_contracts
RUN chown -R appuser:appuser /app

USER appuser
ENV PYTHONPATH="/app"
CMD ["python", "-u", "/app/bridge.py"]
