SELECT s.nom AS fournisseur, sum(f.quantite) AS quantite_achetee
FROM odoo_analytics.fact_achats AS f
LEFT JOIN odoo_analytics.dim_fournisseur AS s ON s.fournisseur_id = f.fournisseur_id
GROUP BY f.fournisseur_id, fournisseur ORDER BY quantite_achetee DESC LIMIT 10
