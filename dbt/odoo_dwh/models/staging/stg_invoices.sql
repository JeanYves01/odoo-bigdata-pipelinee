{{ config(materialized='view') }}
select toUInt32(id) as invoice_id, name as invoice_number,
       lowerUTF8(move_type) as invoice_type, toUInt32(partner_id) as partner_id,
       toDateTime(invoice_date) as invoice_date, toFloat64(total_amount) as total_amount,
       lowerUTF8(state) as status, toDateTime(create_date) as create_date,
       toDateTime(write_date) as write_date
from {{ source('odoo_raw', 'account_move') }}
where id > 0 and lowerUTF8(move_type) in ('in_invoice','out_invoice')
  and lowerUTF8(state) in ('draft','posted','paid','cancel')
qualify row_number() over (partition by id order by write_date desc) = 1
