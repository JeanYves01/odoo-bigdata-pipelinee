SELECT toStartOfMonth(toDate(f.date)) AS mois,count() AS nombre_mouvements
FROM odoo_analytics.fact_stocks AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
LEFT JOIN odoo_analytics.dim_entrepot AS e ON e.entrepot_id = f.entrepot_id
WHERE 1=1
[[AND toDate(f.date) >= toDate({{date_from}})]]
[[AND toDate(f.date) <= toDate({{date_to}})]]
[[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]]
[[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
[[AND positionCaseInsensitiveUTF8(e.nom, {{warehouse}}) > 0]]
GROUP BY mois
ORDER BY mois
