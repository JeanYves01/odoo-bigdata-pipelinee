{{ config(materialized='table', engine='MergeTree()', order_by='fournisseur_id') }}
select p.partner_id as fournisseur_id, p.partner_name as nom,
       coalesce(p.country, 'Inconnu') as pays,
       CAST(NULL AS Nullable(Float64)) as delai_moyen_jours
from {{ ref('stg_partners') }} p
where p.partner_id in (select distinct supplier_id from {{ ref('stg_purchase_orders') }})
