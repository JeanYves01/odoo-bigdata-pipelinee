{{ config(materialized='view') }}
select m.stock_move_id, m.product_id, p.product_name, p.category_id,
       m.quantity, m.move_type, m.reference, m.move_date, m.status
from {{ ref('stg_stock_moves') }} m
inner join {{ ref('stg_products') }} p on m.product_id = p.product_id
where m.status = 'done'
