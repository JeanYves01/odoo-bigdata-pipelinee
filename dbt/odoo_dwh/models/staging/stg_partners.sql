{{ config(materialized='view') }}
select toUInt32(id) as partner_id, trim(name) as partner_name,
       nullIf(trim(email), '') as email, nullIf(trim(phone), '') as phone,
       nullIf(trim(city), '') as city, nullIf(trim(country), '') as country,
       toUInt8(is_company) as is_company, toDateTime(create_date) as create_date
from {{ source('odoo_raw', 'res_partner') }}
where id > 0 and notEmpty(trim(name))
qualify row_number() over (partition by id order by create_date desc) = 1
