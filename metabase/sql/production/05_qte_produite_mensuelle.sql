SELECT toStartOfMonth(date) AS mois, sum(qte_produite) AS quantite_produite
FROM odoo_analytics.fact_production WHERE statut = 'done'
GROUP BY mois ORDER BY mois
