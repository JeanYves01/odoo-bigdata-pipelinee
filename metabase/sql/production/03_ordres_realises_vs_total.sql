SELECT if(statut = 'done', 'Termines', 'Non termines') AS statut_synthetique,
       count() AS nombre_ordres
FROM odoo_analytics.fact_production
GROUP BY statut_synthetique ORDER BY statut_synthetique
