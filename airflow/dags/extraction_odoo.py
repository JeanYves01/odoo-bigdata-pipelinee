"""Extraction PostgreSQL simule Odoo vers ClickHouse Raw, avec curseur incremental.

Tables de reference (res_partner, categories, produits): rechargement complet.
Tables transactionnelles: premier run complet, puis filtre sur write_date/create_date.
Les vues dbt staging dedoublonnent les reprises de batch par cle metier.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

import pendulum
import psycopg2
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from clickhouse_driver import Client

LOG = logging.getLogger(__name__)

PG_CONFIG = {
    "host": "odoo_postgres",
    "port": 5432,
    "dbname": "odoo_db",
    "user": "odoo",
    "password": "odoo123",
    "connect_timeout": 10,
}
CH_CONFIG = {
    "host": os.getenv("CLICKHOUSE_HOST", "clickhouse_dwh"),
    "port": int(os.getenv("CLICKHOUSE_PORT", "9000")),
    "user": os.getenv("CLICKHOUSE_USER", "default"),
    "password": os.getenv("CLICKHOUSE_PASSWORD", ""),
    "database": "odoo_analytics",
    "send_receive_timeout": 300,
}

# raw_name, postgres table, columns, reference/full-refresh, watermark column
TABLES = {
    "partners": ("raw_res_partner", "res_partner",
                 ["id", "name", "email", "phone", "city", "country", "is_company", "create_date"], True, "create_date"),
    "categories": ("raw_product_category", "product_category",
                    ["id", "name", "create_date"], True, "create_date"),
    "products": ("raw_product_template", "product_template",
                  ["id", "name", "categ_id", "list_price", "standard_price", "create_date"], True, "create_date"),
    "sale_orders": ("raw_sale_order", "sale_order",
                     ["id", "name", "partner_id", "order_date", "total_amount", "state", "create_date", "write_date"], False, "write_date"),
    "sale_order_lines": ("raw_sale_order_line", "sale_order_line",
                          ["id", "order_id", "product_id", "quantity", "unit_price", "line_amount", "create_date"], False, "create_date"),
    "purchase_orders": ("raw_purchase_order", "purchase_order",
                         ["id", "name", "partner_id", "order_date", "total_amount", "state", "create_date", "write_date"], False, "write_date"),
    "purchase_order_lines": ("raw_purchase_order_line", "purchase_order_line",
                              ["id", "order_id", "product_id", "quantity", "unit_price", "line_amount", "create_date"], False, "create_date"),
    "mrp_production": ("raw_mrp_production", "mrp_production",
                       ["id", "name", "product_id", "product_qty", "scheduled_start_date", "start_date", "end_date", "duration", "state", "create_date"], False, "create_date"),
    "stock_moves": ("raw_stock_move", "stock_move",
                     ["id", "product_id", "quantity", "move_type", "reference", "move_date", "state", "create_date"], False, "create_date"),
    "invoices": ("raw_account_move", "account_move",
                 ["id", "name", "move_type", "partner_id", "invoice_date", "total_amount", "state", "create_date", "write_date"], False, "write_date"),
}


def extract_table(table_key: str, **context) -> None:
    """Extract une table, charge Raw puis ne met a jour le watermark qu'apres succes."""
    raw_table, source_table, columns, is_reference, watermark_col = TABLES[table_key]
    cursor_key = f"odoo_extract_watermark_{table_key}"
    conn = None
    ch = None
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        with conn.cursor() as cur:
            cursor_value = None if is_reference else Variable.get(cursor_key, default_var=None)
            quoted_columns = ", ".join(f'"{column}"' for column in columns)
            if cursor_value:
                query = (
                    f'SELECT {quoted_columns} FROM public."{source_table}" '
                    f'WHERE "{watermark_col}" > %s ORDER BY "{watermark_col}", id'
                )
                cur.execute(query, (cursor_value,))
            else:
                query = f'SELECT {quoted_columns} FROM public."{source_table}" ORDER BY id'
                cur.execute(query)
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]

        ch = Client(**CH_CONFIG)
        if is_reference:
            # Les petites dimensions de reference sont un snapshot complet a chaque run.
            ch.execute(f"TRUNCATE TABLE {CH_CONFIG['database']}.{raw_table}")
        if rows:
            insert_columns = ", ".join(f"`{c}`" for c in col_names)
            ch.execute(
                f"INSERT INTO {CH_CONFIG['database']}.{raw_table} ({insert_columns}) VALUES",
                rows,
            )
            LOG.info("Loaded %s rows into %s", len(rows), raw_table)
        else:
            LOG.info("No new rows for %s", source_table)

        # Le pointeur avance seulement apres le chargement ClickHouse reussi.
        if not is_reference and rows:
            watermark_index = col_names.index(watermark_col)
            latest = max(row[watermark_index] for row in rows)
            Variable.set(cursor_key, latest.isoformat(sep=" "))
        LOG.info("Extraction %s terminee, %s ligne(s)", source_table, len(rows))
    finally:
        if conn is not None:
            conn.close()
        if ch is not None:
            ch.disconnect()


def make_extract_task(key: str) -> PythonOperator:
    return PythonOperator(
        task_id=f"extract_{key}",
        python_callable=extract_table,
        op_kwargs={"table_key": key},
    )


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": pendulum.duration(minutes=5),
}

with DAG(
    dag_id="extraction_odoo",
    description="Extracte les 10 tables PostgreSQL Odoo vers ClickHouse Raw puis declenche dbt.",
    default_args=default_args,
    start_date=pendulum.datetime(2024, 1, 1, tz="Africa/Abidjan"),
    schedule="0 0 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["odoo", "extract", "clickhouse"],
) as dag:
    extract_partners = make_extract_task("partners")
    extract_categories = make_extract_task("categories")
    extract_products = make_extract_task("products")
    extract_sale_orders = make_extract_task("sale_orders")
    extract_sale_lines = make_extract_task("sale_order_lines")
    extract_purchase_orders = make_extract_task("purchase_orders")
    extract_purchase_lines = make_extract_task("purchase_order_lines")
    extract_mrp = make_extract_task("mrp_production")
    extract_stock = make_extract_task("stock_moves")
    extract_invoices = make_extract_task("invoices")
    trigger_dbt = TriggerDagRunOperator(
        task_id="trigger_dbt",
        trigger_dag_id="transformation_dbt",
        wait_for_completion=False,
        reset_dag_run=False,
    )
    (
        extract_partners
        >> extract_categories
        >> extract_products
        >> extract_sale_orders
        >> extract_sale_lines
        >> extract_purchase_orders
        >> extract_purchase_lines
        >> extract_mrp
        >> extract_stock
        >> extract_invoices
        >> trigger_dbt
    )
