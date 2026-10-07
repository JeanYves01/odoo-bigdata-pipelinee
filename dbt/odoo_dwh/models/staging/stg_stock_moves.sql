{{ config(materialized='view') }}
select toUInt32(id) as stock_move_id, toUInt32(product_id) as product_id,
       toFloat64(quantity) as quantity, lowerUTF8(move_type) as move_type,
       reference, toDateTime(move_date) as move_date, lowerUTF8(state) as status,
       toDateTime(create_date) as create_date
from {{ source('odoo_raw', 'stock_move') }}
where id > 0 and product_id > 0 and quantity > 0
  and lowerUTF8(move_type) in ('in','out') and lowerUTF8(state) in ('done','cancel')
qualify row_number() over (partition by id order by create_date desc) = 1
