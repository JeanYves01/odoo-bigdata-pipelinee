SELECT f.status AS statut, uniqExact(f.purchase_order_id) AS nombre_commandes
FROM odoo_analytics.int_achats_enrichis AS f
LEFT JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
LEFT JOIN odoo_analytics.dim_fournisseur AS s ON s.fournisseur_id = f.supplier_id
WHERE 1=1
[[AND toDate(f.order_date) >= toDate({{date_from}})]]
[[AND toDate(f.order_date) <= toDate({{date_to}})]]
[[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]]
[[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
[[AND positionCaseInsensitiveUTF8(s.nom, {{supplier}}) > 0]]
GROUP BY f.status ORDER BY nombre_commandes DESC
