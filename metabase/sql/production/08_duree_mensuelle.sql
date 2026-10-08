SELECT toStartOfMonth(date) AS mois,
       round(avgIf(duree_fabrication_heures, statut = 'done'), 2) AS duree_moyenne_heures
FROM odoo_analytics.fact_production WHERE statut = 'done'
GROUP BY mois ORDER BY mois
