{{ config(materialized='view') }}
select
    l.purchase_order_line_id as purchase_order_line_id,
    o.purchase_order_id as purchase_order_id,
    o.order_number as order_number,
    o.order_date as order_date,
    o.supplier_id as supplier_id,
    l.product_id as product_id,
    p.product_name as product_name,
    p.category_id as category_id,
    l.quantity as quantity,
    l.unit_price as unit_price,
    l.line_amount as montant,
    o.status as status,
    -- La source simulee n'a pas de date de reception: ne pas inventer un delai.
    CAST(NULL AS Nullable(Int32)) as delai_livraison_jours
from {{ ref('stg_purchase_order_lines') }} as l
inner join {{ ref('stg_purchase_orders') }} as o
    on l.purchase_order_id = o.purchase_order_id
inner join {{ ref('stg_products') }} as p
    on l.product_id = p.product_id
where o.status in ('confirmed', 'received')
