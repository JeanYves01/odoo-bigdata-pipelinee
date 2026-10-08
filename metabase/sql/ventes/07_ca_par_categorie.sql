SELECT p.categorie, round(sum(f.chiffre_affaires), 2) AS ca
FROM odoo_analytics.fact_ventes AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
GROUP BY p.categorie ORDER BY ca DESC
