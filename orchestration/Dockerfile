FROM apache/airflow:3.1.8

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow-providers-amazon" \
    "apache-airflow-providers-apache-beam[common.compat]" \
    "apache-airflow-providers-apache-flink" \
    "apache-airflow-providers-apache-kafka" \
    "apache-airflow-providers-fab" \
    "apache-airflow-providers-postgres" \
    "apache-airflow-providers-redis" \
    "apache-airflow[statsd]==${AIRFLOW_VERSION}" \
    "boto3" \
    "cachetools>=6.0" \
    "kafka-python" \
    "psycopg[binary]" \
    "requests" \
    --constraint "${HOME}/constraints.txt"
