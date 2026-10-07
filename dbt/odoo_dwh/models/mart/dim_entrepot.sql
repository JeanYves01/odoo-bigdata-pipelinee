{{ config(materialized='table', engine='MergeTree()', order_by='entrepot_id') }}
-- Les mouvements sources ne possedent pas d'identifiant d'entrepot.
-- Dimension unique et explicite pour ne pas attribuer des sites fictifs aux mouvements.
select toUInt32(1) as entrepot_id, 'Entrepot principal (simule)' as nom,
       'Abidjan' as ville, 'Zone unique simulee' as zone
