SELECT round(sum(f.chiffre_affaires) / nullIf(uniqExact(f.sale_order_id), 0), 2) AS panier_moyen
FROM odoo_analytics.fact_ventes AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
LEFT JOIN odoo_analytics.dim_client AS c ON c.client_id = f.client_id
WHERE 1=1
[[AND toDate(f.date) >= toDate({{date_from}})]]
[[AND toDate(f.date) <= toDate({{date_to}})]]
[[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]]
[[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
[[AND positionCaseInsensitiveUTF8(c.nom, {{client}}) > 0]]
