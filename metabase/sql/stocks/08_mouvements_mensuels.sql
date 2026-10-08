SELECT toStartOfMonth(date) AS mois, count() AS nombre_mouvements
FROM odoo_analytics.fact_stocks GROUP BY mois ORDER BY mois
