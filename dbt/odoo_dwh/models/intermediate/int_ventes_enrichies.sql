{{ config(materialized='view') }}
select
    l.sale_order_line_id as sale_order_line_id,
    o.sale_order_id as sale_order_id,
    o.order_number as order_number,
    o.order_date as order_date,
    o.customer_id as customer_id,
    l.product_id as product_id,
    p.product_name as product_name,
    p.category_id as category_id,
    l.quantity as quantity,
    l.unit_price as unit_price,
    l.line_amount as chiffre_affaires,
    round(l.line_amount - l.quantity * p.standard_price, 2) as marge_brute,
    o.status as status
from {{ ref('stg_sale_order_lines') }} as l
inner join {{ ref('stg_sale_orders') }} as o
    on l.sale_order_id = o.sale_order_id
inner join {{ ref('stg_products') }} as p
    on l.product_id = p.product_id
where o.status in ('confirmed', 'done')
