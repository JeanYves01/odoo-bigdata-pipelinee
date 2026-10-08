SELECT p.categorie, round(sum(f.montant), 2) AS montant_achats
FROM odoo_analytics.fact_achats AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
GROUP BY p.categorie ORDER BY montant_achats DESC
