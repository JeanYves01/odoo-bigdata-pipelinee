{{ config(materialized='view') }}
select toUInt32(id) as category_id, trim(name) as category_name,
       toDateTime(create_date) as create_date
from {{ source('odoo_raw', 'product_category') }}
where id > 0 and notEmpty(trim(name))
qualify row_number() over (partition by id order by create_date desc) = 1
