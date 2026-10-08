WITH dernier_solde AS (
  SELECT product_id, argMax(solde, tuple(date, stock_move_id)) AS qte_stock
  FROM odoo_analytics.fact_stocks GROUP BY product_id
)
SELECT e.nom AS entrepot, sum(d.qte_stock) AS quantite_stock,
       round(sum(d.qte_stock * p.cout), 2) AS valeur_stock_estimee
FROM dernier_solde AS d
INNER JOIN odoo_analytics.dim_produit AS p ON p.product_id = d.product_id
CROSS JOIN odoo_analytics.dim_entrepot AS e
GROUP BY e.entrepot_id, entrepot
