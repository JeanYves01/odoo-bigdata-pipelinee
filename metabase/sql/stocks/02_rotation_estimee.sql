-- Proxy: COGS des ventes / moyenne des valorisations mensuelles observees.
-- Stock de fin de mois ne couvre que les produits ayant eu un mouvement ce mois;
-- ce n'est pas un snapshot exhaustif d'inventaire.
WITH monthly_product_balance AS (
  SELECT toStartOfMonth(date) AS mois, product_id,
         argMax(solde, tuple(date, stock_move_id)) AS qte_stock
  FROM odoo_analytics.fact_stocks
  GROUP BY mois, product_id
), monthly_stock_value AS (
  SELECT b.mois, sum(b.qte_stock * p.cout) AS valeur
  FROM monthly_product_balance AS b
  INNER JOIN odoo_analytics.dim_produit AS p ON p.product_id = b.product_id
  GROUP BY b.mois
), cogs AS (
  SELECT sum(f.quantite * p.cout) AS cout_ventes
  FROM odoo_analytics.fact_ventes AS f
  INNER JOIN odoo_analytics.dim_produit AS p ON p.product_id = f.product_id
)
SELECT round(c.cout_ventes / nullIf(avg(v.valeur), 0), 2) AS rotation_estimee_proxy
FROM cogs AS c CROSS JOIN monthly_stock_value AS v
GROUP BY c.cout_ventes
