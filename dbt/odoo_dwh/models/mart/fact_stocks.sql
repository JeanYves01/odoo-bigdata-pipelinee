{{ config(materialized='table', engine='ReplacingMergeTree()',
          order_by='(date_id, stock_move_id)',
          partition_by='toYYYYMM(date)') }}
with movements as (
    select s.stock_move_id, s.product_id,
           toUInt32(toYYYYMMDD(toDate(s.move_date))) as date_id,
           toDate(s.move_date) as date,
           if(s.move_type = 'in', s.quantity, 0.) as qte_entree,
           if(s.move_type = 'out', s.quantity, 0.) as qte_sortie
    from {{ ref('int_stocks_enrichis') }} s
)
select stock_move_id, product_id, toUInt32(1) as entrepot_id, date_id, date,
       qte_entree, qte_sortie,
       sum(qte_entree - qte_sortie) over (
           partition by product_id order by date, stock_move_id
           rows between unbounded preceding and current row
       ) as solde
from movements
