{{ config(materialized='table', engine='ReplacingMergeTree()',
          order_by='(date_id, sale_order_line_id)',
          partition_by='toYYYYMM(date)') }}
select v.sale_order_line_id, v.sale_order_id, v.product_id,
       v.customer_id as client_id,
       toUInt32(toYYYYMMDD(toDate(v.order_date))) as date_id,
       toDate(v.order_date) as date,
       v.quantity as quantite, v.chiffre_affaires, v.marge_brute
from {{ ref('int_ventes_enrichies') }} v
