{{ config(materialized='table', engine='MergeTree()', order_by='client_id') }}
select p.partner_id as client_id, p.partner_name as nom,
       'Non renseigne' as secteur, coalesce(p.city, 'Inconnue') as ville,
       coalesce(p.country, 'Inconnu') as pays
from {{ ref('stg_partners') }} p
where p.partner_id in (select distinct customer_id from {{ ref('stg_sale_orders') }})
