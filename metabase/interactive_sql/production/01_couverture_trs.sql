SELECT round(100.0 * countIf(f.trs IS NOT NULL) / nullIf(count(), 0), 2) AS couverture_trs_pct
FROM odoo_analytics.fact_production AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
WHERE 1=1
[[AND toDate(f.date) >= toDate({{date_from}})]]
[[AND toDate(f.date) <= toDate({{date_to}})]]
[[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]]
[[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
[[AND positionCaseInsensitiveUTF8(f.statut, {{status}}) > 0]]
