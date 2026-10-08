SELECT toStartOfMonth(date) AS mois, round(sum(marge_brute), 2) AS marge_brute
FROM odoo_analytics.fact_ventes
GROUP BY mois ORDER BY mois
