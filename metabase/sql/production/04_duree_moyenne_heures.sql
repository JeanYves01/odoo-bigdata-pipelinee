SELECT round(avgIf(duree_fabrication_heures, statut = 'done'), 2) AS duree_moyenne_heures_ordres_termines
FROM odoo_analytics.fact_production
