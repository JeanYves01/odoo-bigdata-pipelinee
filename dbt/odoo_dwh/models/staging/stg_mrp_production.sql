{{ config(materialized='view') }}
select toUInt32(id) as production_id, name as production_number,
       toUInt32(product_id) as product_id, toFloat64(product_qty) as product_qty,
       toDateTime(scheduled_start_date) as scheduled_start_date,
       start_date, end_date, toFloat64(duration) as duration_hours,
       lowerUTF8(state) as status, toDateTime(create_date) as create_date
from {{ source('odoo_raw', 'mrp_production') }}
where id > 0 and product_id > 0 and lowerUTF8(state) in ('confirmed','in_progress','done','cancel')
qualify row_number() over (partition by id order by create_date desc) = 1
