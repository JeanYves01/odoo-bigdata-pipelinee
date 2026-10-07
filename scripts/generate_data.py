"""Genere 21 370 lignes de donnees industrielles fictives PostgreSQL/Odoo.

Execution: python scripts/generate_data.py
Variables facultatives: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME.
ATTENTION: chaque execution reinitialise les 10 tables sources du simulateur.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from random import Random

from faker import Faker
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table,
    create_engine, insert, text,
)
from sqlalchemy.engine import Engine

DB_USER = os.getenv("DB_USER", "odoo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "odoo123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "odoo_db")
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}?client_encoding=utf8"
)

SEED = 42
rng = Random(SEED)
fake = Faker("fr_FR")
Faker.seed(SEED)
metadata = MetaData()

# Des champs assez larges pour les valeurs generees par Faker, notamment les telephones.
res_partner = Table(
    "res_partner", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False),
    Column("email", String(254)),
    Column("phone", String(50)),
    Column("city", String(100)),
    Column("country", String(80)),
    Column("is_company", Integer, nullable=False, default=1),
    Column("create_date", DateTime, nullable=False),
)
product_category = Table(
    "product_category", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("create_date", DateTime, nullable=False),
)
product_template = Table(
    "product_template", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False),
    Column("categ_id", Integer, ForeignKey("product_category.id")),
    Column("list_price", Float, nullable=False),
    Column("standard_price", Float, nullable=False),
    Column("create_date", DateTime, nullable=False),
)
sale_order = Table(
    "sale_order", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("partner_id", Integer, ForeignKey("res_partner.id")),
    Column("order_date", DateTime, nullable=False),
    Column("total_amount", Float, nullable=False),
    Column("state", String(20), nullable=False),
    Column("create_date", DateTime, nullable=False),
    Column("write_date", DateTime, nullable=False),
)
sale_order_line = Table(
    "sale_order_line", metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("sale_order.id"), nullable=False),
    Column("product_id", Integer, ForeignKey("product_template.id"), nullable=False),
    Column("quantity", Float, nullable=False),
    Column("unit_price", Float, nullable=False),
    Column("line_amount", Float, nullable=False),
    Column("create_date", DateTime, nullable=False),
)
purchase_order = Table(
    "purchase_order", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("partner_id", Integer, ForeignKey("res_partner.id")),
    Column("order_date", DateTime, nullable=False),
    Column("total_amount", Float, nullable=False),
    Column("state", String(20), nullable=False),
    Column("create_date", DateTime, nullable=False),
    Column("write_date", DateTime, nullable=False),
)
purchase_order_line = Table(
    "purchase_order_line", metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("purchase_order.id"), nullable=False),
    Column("product_id", Integer, ForeignKey("product_template.id"), nullable=False),
    Column("quantity", Float, nullable=False),
    Column("unit_price", Float, nullable=False),
    Column("line_amount", Float, nullable=False),
    Column("create_date", DateTime, nullable=False),
)
mrp_production = Table(
    "mrp_production", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("product_id", Integer, ForeignKey("product_template.id"), nullable=False),
    Column("product_qty", Float, nullable=False),
    Column("scheduled_start_date", DateTime, nullable=False),
    Column("start_date", DateTime),
    Column("end_date", DateTime),
    Column("duration", Float, nullable=False),
    Column("state", String(20), nullable=False),
    Column("create_date", DateTime, nullable=False),
)
stock_move = Table(
    "stock_move", metadata,
    Column("id", Integer, primary_key=True),
    Column("product_id", Integer, ForeignKey("product_template.id"), nullable=False),
    Column("quantity", Float, nullable=False),
    Column("move_type", String(20), nullable=False),
    Column("reference", String(50), nullable=False),
    Column("move_date", DateTime, nullable=False),
    Column("state", String(20), nullable=False),
    Column("create_date", DateTime, nullable=False),
)
account_move = Table(
    "account_move", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("move_type", String(20), nullable=False),
    Column("partner_id", Integer, ForeignKey("res_partner.id")),
    Column("invoice_date", DateTime, nullable=False),
    Column("total_amount", Float, nullable=False),
    Column("state", String(20), nullable=False),
    Column("create_date", DateTime, nullable=False),
    Column("write_date", DateTime, nullable=False),
)

TABLES = [res_partner, product_category, product_template, sale_order,
          sale_order_line, purchase_order, purchase_order_line,
          mrp_production, stock_move, account_move]
COUNTS = {
    "res_partner": 200, "product_category": 20, "product_template": 150,
    "sale_order": 2000, "sale_order_line": 8000,
    "purchase_order": 800, "purchase_order_line": 3200,
    "mrp_production": 500, "stock_move": 5000, "account_move": 1500,
}
START = datetime(2024, 1, 1)
END = datetime(2025, 12, 31, 23, 59, 59)


def rand_date() -> datetime:
    seconds = int((END - START).total_seconds())
    return START + timedelta(seconds=rng.randint(0, seconds))


def money(low: float, high: float) -> float:
    return round(rng.uniform(low, high), 2)


def insert_rows(conn, table: Table, rows: list[dict]) -> None:
    if rows:
        conn.execute(insert(table), rows)


def generate(engine: Engine) -> dict[str, int]:
    """Recree les tables simulees puis les remplit dans une transaction."""
    print("[...] Creation/reinitialisation des 10 tables sources...")
    metadata.drop_all(engine, checkfirst=True)
    metadata.create_all(engine)

    now = datetime.now()
    categories = [
        {"id": i, "name": name, "create_date": now}
        for i, name in enumerate([
            "Matières premières", "Composants électriques", "Métal",
            "Plastique", "Emballage", "Outillage", "Machines",
            "Pièces de rechange", "Sécurité", "Électronique",
            "Hydraulique", "Pneumatique", "Énergie", "Peinture",
            "Fixations", "Câblage", "Capteurs", "Consommables",
            "Produits finis", "Divers",
        ], start=1)
    ]
    countries = ["Côte d'Ivoire", "Mali", "Sénégal", "Burkina Faso", "Ghana"]
    partners = []
    for i in range(1, 201):
        partners.append({
            "id": i, "name": fake.company() if i % 3 == 0 else fake.name(),
            "email": fake.email(), "phone": fake.phone_number()[:50],
            "city": fake.city()[:100], "country": rng.choice(countries),
            "is_company": 1 if i % 3 == 0 else 0, "create_date": now,
        })
    products = []
    for i in range(1, 151):
        cost = money(20, 3000)
        products.append({
            "id": i, "name": f"{fake.word().capitalize()} {i:03d}",
            "categ_id": rng.randint(1, 20), "list_price": round(cost * rng.uniform(1.2, 2.5), 2),
            "standard_price": cost, "create_date": now,
        })

    sale_orders, sale_lines = [], []
    for order_id in range(1, 2001):
        dt = rand_date()
        partner_id = rng.randint(1, 200)
        lines = []
        for _ in range(4):
            prod = products[rng.randrange(len(products))]
            qty, price = round(rng.uniform(1, 20), 2), prod["list_price"]
            lines.append({"product_id": prod["id"], "quantity": qty,
                          "unit_price": price, "line_amount": round(qty * price, 2)})
        total = round(sum(x["line_amount"] for x in lines), 2)
        sale_orders.append({"id": order_id, "name": f"SO{2024000 + order_id}",
                            "partner_id": partner_id, "order_date": dt,
                            "total_amount": total, "state": rng.choice(["draft", "confirmed", "done", "cancel"]),
                            "create_date": dt, "write_date": dt})
        for line_no, line in enumerate(lines, start=1):
            sale_lines.append({"id": (order_id - 1) * 4 + line_no, "order_id": order_id,
                               **line, "create_date": dt})

    purchase_orders, purchase_lines = [], []
    supplier_ids = list(range(1, 201))
    for order_id in range(1, 801):
        dt = rand_date()
        lines = []
        for _ in range(4):
            prod = products[rng.randrange(len(products))]
            qty, price = round(rng.uniform(1, 50), 2), prod["standard_price"]
            lines.append({"product_id": prod["id"], "quantity": qty,
                          "unit_price": price, "line_amount": round(qty * price, 2)})
        total = round(sum(x["line_amount"] for x in lines), 2)
        purchase_orders.append({"id": order_id, "name": f"PO{2024000 + order_id}",
                                "partner_id": rng.choice(supplier_ids), "order_date": dt,
                                "total_amount": total, "state": rng.choice(["draft", "confirmed", "received", "cancel"]),
                                "create_date": dt, "write_date": dt})
        for line_no, line in enumerate(lines, start=1):
            purchase_lines.append({"id": (order_id - 1) * 4 + line_no, "order_id": order_id,
                                   **line, "create_date": dt})

    productions = []
    for i in range(1, 501):
        dt = rand_date()
        duration = round(rng.uniform(1, 48), 2)
        state = rng.choice(["confirmed", "in_progress", "done", "cancel"])
        productions.append({
            "id": i, "name": f"MO{2024000 + i}", "product_id": rng.randint(1, 150),
            "product_qty": round(rng.uniform(10, 100), 2), "scheduled_start_date": dt,
            "start_date": dt if state in ("in_progress", "done") else None,
            "end_date": dt + timedelta(hours=duration) if state == "done" else None,
            "duration": duration if state == "done" else 0.0,
            "state": state, "create_date": dt,
        })
    moves = []
    for i in range(1, 5001):
        dt = rand_date()
        moves.append({"id": i, "product_id": rng.randint(1, 150),
                      "quantity": round(rng.uniform(1, 100), 2),
                      "move_type": rng.choice(["in", "out"]), "reference": f"SM{2024000 + i}",
                      "move_date": dt, "state": rng.choice(["done", "cancel"]), "create_date": dt})
    invoices = []
    for i in range(1, 1501):
        dt = rand_date()
        invoices.append({"id": i, "name": f"INV{2024000 + i}",
                         "move_type": rng.choice(["in_invoice", "out_invoice"]),
                         "partner_id": rng.randint(1, 200), "invoice_date": dt,
                         "total_amount": money(100, 10000),
                         "state": rng.choice(["draft", "posted", "paid", "cancel"]),
                         "create_date": dt, "write_date": dt})

    data = [partners, categories, products, sale_orders, sale_lines,
            purchase_orders, purchase_lines, productions, moves, invoices]
    print("[...] Insertion des enregistrements...")
    with engine.begin() as conn:
        for table, rows in zip(TABLES, data):
            insert_rows(conn, table, rows)

    with engine.connect() as conn:
        actual = {}
        for table in TABLES:
            actual[table.name] = conn.execute(text(f'SELECT COUNT(*) FROM "{table.name}"')).scalar_one()
    return actual


def main() -> int:
    engine = None
    try:
        print("=" * 60)
        print("GENERATEUR DE DONNEES ODOO FICTIVES")
        print("=" * 60)
        print(f"Connexion : {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        print("ATTENTION : les 10 tables du simulateur seront reinitialisees.")
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 10})
        counts = generate(engine)
        total = 0
        print("\nVERIFICATION DES DONNEES")
        print("-" * 45)
        for name, expected in COUNTS.items():
            actual = counts[name]
            total += actual
            status = "OK" if actual == expected else "ERREUR"
            print(f"[{status}] {name:<24} {actual:>6} (attendu {expected})")
        print("-" * 45)
        print(f"TOTAL                     {total:>6} / 21370")
        if total != 21370 or any(counts[k] != v for k, v in COUNTS.items()):
            print("ERREUR : nombre de lignes inattendu.")
            return 1
        print("SUCCESS : 21 370 lignes generees, integrite verifiee.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"\nERREUR : {exc}", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
