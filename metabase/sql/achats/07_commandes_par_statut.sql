SELECT status AS statut, uniqExact(purchase_order_id) AS nombre_commandes
FROM odoo_analytics.int_achats_enrichis
GROUP BY status ORDER BY nombre_commandes DESC
