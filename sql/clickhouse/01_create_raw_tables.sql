-- Etape 6: database analytique et tables brutes pour le chargement Airflow.
-- Source de verite des colonnes: scripts/generate_data.py (etape 4).
-- Idempotent: CREATE DATABASE/TABLE IF NOT EXISTS ne supprime aucune donnee.

CREATE DATABASE IF NOT EXISTS odoo_analytics;

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_res_partner
(
    id UInt32,
    name String,
    email Nullable(String),
    phone Nullable(String),
    city Nullable(String),
    country Nullable(String),
    is_company UInt8,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_product_category
(
    id UInt32,
    name String,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_product_template
(
    id UInt32,
    name String,
    categ_id Nullable(UInt32),
    list_price Float64,
    standard_price Float64,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_sale_order
(
    id UInt32,
    name String,
    partner_id Nullable(UInt32),
    order_date DateTime,
    total_amount Float64,
    state String,
    create_date DateTime,
    write_date DateTime
)
ENGINE = MergeTree
ORDER BY (order_date, id);

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_sale_order_line
(
    id UInt32,
    order_id UInt32,
    product_id UInt32,
    quantity Float64,
    unit_price Float64,
    line_amount Float64,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY (order_id, id);

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_purchase_order
(
    id UInt32,
    name String,
    partner_id Nullable(UInt32),
    order_date DateTime,
    total_amount Float64,
    state String,
    create_date DateTime,
    write_date DateTime
)
ENGINE = MergeTree
ORDER BY (order_date, id);

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_purchase_order_line
(
    id UInt32,
    order_id UInt32,
    product_id UInt32,
    quantity Float64,
    unit_price Float64,
    line_amount Float64,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY (order_id, id);

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_mrp_production
(
    id UInt32,
    name String,
    product_id UInt32,
    product_qty Float64,
    scheduled_start_date DateTime,
    start_date Nullable(DateTime),
    end_date Nullable(DateTime),
    duration Float64,
    state String,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY (scheduled_start_date, id);

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_stock_move
(
    id UInt32,
    product_id UInt32,
    quantity Float64,
    move_type String,
    reference String,
    move_date DateTime,
    state String,
    create_date DateTime
)
ENGINE = MergeTree
ORDER BY (move_date, id);

CREATE TABLE IF NOT EXISTS odoo_analytics.raw_account_move
(
    id UInt32,
    name String,
    move_type String,
    partner_id Nullable(UInt32),
    invoice_date DateTime,
    total_amount Float64,
    state String,
    create_date DateTime,
    write_date DateTime
)
ENGINE = MergeTree
ORDER BY (invoice_date, id);
