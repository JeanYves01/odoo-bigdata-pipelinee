# Image Airflow personnalisee pour odoo-bigdata-pipeline
FROM apache/airflow:2.9.3-python3.11

# dbt debug verifie la disponibilite de Git. Installer Git en root, puis
# revenir a l'utilisateur non-root airflow pour pip et l'execution des DAGs.
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

USER airflow

# Paquets supplementaires dans l'environnement Airflow
COPY requirements-airflow.txt /tmp/requirements-airflow.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements-airflow.txt

# dbt dans un environnement virtuel isole, pour eviter les conflits Airflow/dbt
RUN python -m venv /home/airflow/dbt_venv \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir --upgrade pip \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir "dbt-core==1.11.*" "dbt-clickhouse==1.10.1" \
 && mkdir -p /home/airflow/.local/bin \
 && ln -sf /home/airflow/dbt_venv/bin/dbt /home/airflow/.local/bin/dbt

ENV DBT_BIN=/home/airflow/dbt_venv/bin/dbt
