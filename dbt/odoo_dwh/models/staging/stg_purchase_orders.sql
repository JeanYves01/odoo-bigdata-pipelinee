{{ config(materialized='view') }}
select toUInt32(id) as purchase_order_id, name as order_number,
       toUInt32(partner_id) as supplier_id, toDateTime(order_date) as order_date,
       toFloat64(total_amount) as total_amount, lowerUTF8(state) as status,
       toDateTime(create_date) as create_date, toDateTime(write_date) as write_date
from {{ source('odoo_raw', 'purchase_order') }}
where id > 0 and lowerUTF8(state) in ('draft','confirmed','received','cancel')
qualify row_number() over (partition by id order by write_date desc) = 1
