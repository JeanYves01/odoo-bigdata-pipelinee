"""Orchestre dbt staging -> intermediate -> mart -> tests."""
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/dbt/odoo_dwh"
PROFILES_DIR = "/opt/airflow/dbt/odoo_dwh"
DBT_BIN = "/home/airflow/dbt_venv/bin/dbt"
COMMON = f"--project-dir {PROJECT_DIR} --profiles-dir {PROFILES_DIR}"

with DAG(
    dag_id="transformation_dbt",
    description="Construit les couches dbt staging, intermediate, mart puis execute les tests.",
    start_date=pendulum.datetime(2024, 1, 1, tz="Africa/Abidjan"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["dbt", "clickhouse", "transform"],
) as dag:
    dbt_staging = BashOperator(
        task_id="dbt_staging",
        bash_command=f"cd {PROJECT_DIR} && {DBT_BIN} run {COMMON} --select path:models/staging",
    )
    dbt_intermediate = BashOperator(
        task_id="dbt_intermediate",
        bash_command=f"cd {PROJECT_DIR} && {DBT_BIN} run {COMMON} --select path:models/intermediate",
    )
    dbt_mart = BashOperator(
        task_id="dbt_mart",
        bash_command=f"cd {PROJECT_DIR} && {DBT_BIN} run {COMMON} --select path:models/mart",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT_DIR} && {DBT_BIN} test {COMMON}",
    )
    dbt_staging >> dbt_intermediate >> dbt_mart >> dbt_test
