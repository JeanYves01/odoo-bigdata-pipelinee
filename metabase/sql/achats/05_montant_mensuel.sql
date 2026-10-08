SELECT toStartOfMonth(date) AS mois, round(sum(montant), 2) AS montant_achats
FROM odoo_analytics.fact_achats GROUP BY mois ORDER BY mois
