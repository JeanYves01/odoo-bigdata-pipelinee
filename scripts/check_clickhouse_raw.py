"""Verifie la base analytique et les 10 tables Raw de l'etape 6."""
from clickhouse_driver import Client

client = Client(host="localhost", port=9000, user="default", password="")
expected = {
    "raw_res_partner": 200,
    "raw_product_category": 20,
    "raw_product_template": 150,
    "raw_sale_order": 2000,
    "raw_sale_order_line": 8000,
    "raw_purchase_order": 800,
    "raw_purchase_order_line": 3200,
    "raw_mrp_production": 500,
    "raw_stock_move": 5000,
    "raw_account_move": 1500,
}

databases = {row[0] for row in client.execute("SHOW DATABASES")}
if "odoo_analytics" not in databases:
    raise SystemExit("ERREUR: la base odoo_analytics n'existe pas")

actual_tables = {
    row[0] for row in client.execute("SHOW TABLES FROM odoo_analytics")
}
missing = sorted(set(expected) - actual_tables)
if missing:
    raise SystemExit("ERREUR: tables manquantes: " + ", ".join(missing))

print("Base odoo_analytics : OK")
print("Tables Raw :")
for table, expected_count in expected.items():
    # A cette etape elles sont volontairement vides; le DAG ETL les chargera ensuite.
    count = client.execute(f"SELECT count() FROM odoo_analytics.{table}")[0][0]
    print(f"[OK] {table:<30} {count:>6} lignes (attendu a ce stade: 0)")
print(f"\n[OK] {len(expected)} tables Raw presentes. Elles seront chargees a l'etape 8.")
