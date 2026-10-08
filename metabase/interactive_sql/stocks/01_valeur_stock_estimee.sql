WITH dernier_solde AS (
  SELECT product_id, argMax(solde, tuple(date, stock_move_id)) AS qte_stock, max(date) AS date
  FROM odoo_analytics.fact_stocks GROUP BY product_id
)
SELECT round(sum(d.qte_stock * p.cout), 2) AS valeur_stock_estimee
FROM dernier_solde AS f
INNER JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
LEFT JOIN odoo_analytics.dim_entrepot AS e ON e.entrepot_id = 1
WHERE 1=1
[[AND toDate(f.date) >= toDate({{date_from}})]]
[[AND toDate(f.date) <= toDate({{date_to}})]]
[[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]]
[[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
[[AND positionCaseInsensitiveUTF8(e.nom, {{warehouse}}) > 0]]
