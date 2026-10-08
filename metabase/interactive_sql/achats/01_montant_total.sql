SELECT round(sum(f.montant), 2) AS montant_total_achats
FROM odoo_analytics.fact_achats AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
LEFT JOIN odoo_analytics.dim_fournisseur AS s ON s.fournisseur_id = f.fournisseur_id
WHERE 1=1
[[AND toDate(f.date) >= toDate({{date_from}})]]
[[AND toDate(f.date) <= toDate({{date_to}})]]
[[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]]
[[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
[[AND positionCaseInsensitiveUTF8(s.nom, {{supplier}}) > 0]]
