# ==================================================================
#  Image Airflow personnalisee pour odoo-bigdata-pipeline
#  - Airflow 2.9.3 / Python 3.11
#  - clickhouse-driver dans l'environnement Airflow (DAG d'extraction)
#  - dbt-core + dbt-clickhouse dans un venv ISOLE (evite les conflits
#    de dependances entre Airflow et dbt)
# ==================================================================
FROM apache/airflow:2.9.3-python3.11

USER airflow

# 1) Paquets supplementaires pour Airflow (version d'Airflow verrouillee)
COPY requirements-airflow.txt /tmp/requirements-airflow.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements-airflow.txt

# 2) dbt dans un environnement virtuel separe
RUN python -m venv /home/airflow/dbt_venv \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir --upgrade pip \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir "dbt-core==1.11.*" "dbt-clickhouse==1.10.1" \
 && mkdir -p /home/airflow/.local/bin \
 && ln -sf /home/airflow/dbt_venv/bin/dbt /home/airflow/.local/bin/dbt

ENV DBT_BIN=/home/airflow/dbt_venv/bin/dbt
