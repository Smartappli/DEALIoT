FROM apache/airflow:3.1.8

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow[statsd]==${AIRFLOW_VERSION}" \
    "apache-beam==2.72.0" \
    "psycopg[binary]" \
    "kafka-python" \
    "cachetools>=6.0" \
    "boto3" \
    "requests" \
    "apache-airflow-providers-apache-beam[common.compat]" \
    "apache-airflow-providers-apache-kafka" \
    "apache-airflow-providers-postgres" \
    "apache-airflow-providers-amazon" \
    "apache-airflow-providers-fab" \
    "apache-airflow-providers-redis" \
    "apache-airflow-providers-apache-flink" \
    --constraint "${HOME}/constraints.txt"
