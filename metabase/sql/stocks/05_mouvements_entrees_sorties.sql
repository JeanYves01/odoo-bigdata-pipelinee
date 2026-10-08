SELECT toStartOfMonth(date) AS mois,
       sum(qte_entree) AS quantite_entree,
       sum(qte_sortie) AS quantite_sortie
FROM odoo_analytics.fact_stocks GROUP BY mois ORDER BY mois
