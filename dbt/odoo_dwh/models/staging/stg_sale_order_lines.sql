{{ config(materialized='view') }}
select toUInt32(id) as sale_order_line_id, toUInt32(order_id) as sale_order_id,
       toUInt32(product_id) as product_id, toFloat64(quantity) as quantity,
       toFloat64(unit_price) as unit_price, toFloat64(line_amount) as line_amount,
       toDateTime(create_date) as create_date
from {{ source('odoo_raw', 'sale_order_line') }}
where id > 0 and order_id > 0 and product_id > 0 and quantity > 0
qualify row_number() over (partition by id order by create_date desc) = 1
