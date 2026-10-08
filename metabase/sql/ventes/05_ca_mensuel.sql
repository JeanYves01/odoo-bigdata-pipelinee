SELECT toStartOfMonth(date) AS mois, round(sum(chiffre_affaires), 2) AS ca
FROM odoo_analytics.fact_ventes
GROUP BY mois ORDER BY mois
