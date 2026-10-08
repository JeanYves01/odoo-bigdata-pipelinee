SELECT statut, count() AS nombre_ordres
FROM odoo_analytics.fact_production GROUP BY statut ORDER BY nombre_ordres DESC
