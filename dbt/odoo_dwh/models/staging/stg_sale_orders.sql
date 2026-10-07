{{ config(materialized='view') }}
select toUInt32(id) as sale_order_id, name as order_number,
       toUInt32(partner_id) as customer_id, toDateTime(order_date) as order_date,
       toFloat64(total_amount) as total_amount, lowerUTF8(state) as status,
       toDateTime(create_date) as create_date, toDateTime(write_date) as write_date
from {{ source('odoo_raw', 'sale_order') }}
where id > 0 and lowerUTF8(state) in ('draft','confirmed','done','cancel')
qualify row_number() over (partition by id order by write_date desc) = 1
