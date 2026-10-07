{{ config(materialized='table', engine='MergeTree()', order_by='product_id') }}
select p.product_id, p.product_name as nom, p.category_id,
       coalesce(c.category_name, 'Non classe') as categorie,
       coalesce(c.category_name, 'Non renseignee') as famille,
       p.standard_price as cout, p.list_price as prix_vente
from {{ ref('stg_products') }} p
left join {{ ref('stg_product_categories') }} c on p.category_id = c.category_id
