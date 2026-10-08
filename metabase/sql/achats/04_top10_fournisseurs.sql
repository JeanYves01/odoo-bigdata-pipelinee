SELECT s.nom AS fournisseur, round(sum(f.montant), 2) AS montant_achats
FROM odoo_analytics.fact_achats AS f
LEFT JOIN odoo_analytics.dim_fournisseur AS s ON s.fournisseur_id = f.fournisseur_id
GROUP BY f.fournisseur_id, fournisseur ORDER BY montant_achats DESC LIMIT 10
