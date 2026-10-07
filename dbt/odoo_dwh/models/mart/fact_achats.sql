{{ config(materialized='table', engine='ReplacingMergeTree()',
          order_by='(date_id, purchase_order_line_id)',
          partition_by='toYYYYMM(date)') }}
select a.purchase_order_line_id, a.purchase_order_id, a.product_id,
       a.supplier_id as fournisseur_id,
       toUInt32(toYYYYMMDD(toDate(a.order_date))) as date_id,
       toDate(a.order_date) as date,
       a.quantity as quantite, a.montant, a.delai_livraison_jours as delai_livraison
from {{ ref('int_achats_enrichis') }} a
