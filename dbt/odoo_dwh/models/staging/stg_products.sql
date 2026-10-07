{{ config(materialized='view') }}
select toUInt32(id) as product_id, trim(name) as product_name,
       toUInt32(categ_id) as category_id, toFloat64(list_price) as list_price,
       toFloat64(standard_price) as standard_price, toDateTime(create_date) as create_date
from {{ source('odoo_raw', 'product_template') }}
where id > 0 and categ_id > 0 and notEmpty(trim(name))
qualify row_number() over (partition by id order by create_date desc) = 1
