{{ config(materialized='table', engine='ReplacingMergeTree()',
          order_by='(date_id, production_id)',
          partition_by='toYYYYMM(date)') }}
select p.production_id, p.product_id,
       toUInt32(toYYYYMMDD(toDate(p.scheduled_start_date))) as date_id,
       toDate(p.scheduled_start_date) as date,
       if(p.status = 'done', p.product_qty, 0.) as qte_produite,
       p.duration_hours as duree_fabrication_heures, p.trs, p.status as statut
from {{ ref('int_production_enrichie') }} p
