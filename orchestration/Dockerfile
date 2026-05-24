# syntax=docker/dockerfile:1.7

FROM apache/airflow:3.2.1

USER airflow

COPY --chown=airflow:0 --chmod=0444 orchestration/requirements.txt /tmp/requirements-airflow.txt
COPY --chown=airflow:0 --chmod=0555 dealiot_contracts /opt/airflow/dealiot_contracts
COPY --chown=airflow:0 --chmod=0555 airflow/dags /opt/airflow/dags
COPY --chown=airflow:0 --chmod=0555 pipelines /opt/airflow/pipelines

RUN pip install --no-cache-dir \
    "apache-airflow[statsd]==${AIRFLOW_VERSION}" \
    --requirement /tmp/requirements-airflow.txt \
    --constraint "${HOME}/constraints.txt"

ENV PYTHONPATH="/opt/airflow:${PYTHONPATH}"
