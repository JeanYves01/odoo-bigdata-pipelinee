{{ config(materialized='view') }}
select m.production_id, m.production_number, m.product_id, p.product_name,
       p.category_id, m.product_qty, m.scheduled_start_date,
       m.start_date, m.end_date, m.duration_hours, m.status,
       -- Pas de temps planifie, arrets ni rebuts dans la source: TRS non calculable.
       CAST(NULL AS Nullable(Float64)) as trs
from {{ ref('stg_mrp_production') }} m
inner join {{ ref('stg_products') }} p on m.product_id = p.product_id
