SELECT p.nom AS produit, sum(f.qte_produite) AS quantite_produite
FROM odoo_analytics.fact_production AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
WHERE f.statut = 'done'
GROUP BY f.product_id, produit ORDER BY quantite_produite DESC LIMIT 10
