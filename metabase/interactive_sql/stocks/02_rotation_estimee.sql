WITH ventes AS (
 SELECT round(sum(v.quantite * p.cout), 2) AS cogs FROM odoo_analytics.fact_ventes v
 INNER JOIN odoo_analytics.dim_produit p ON p.product_id=v.product_id
 WHERE 1=1 [[AND toDate(v.date)>=toDate({{date_from}})]] [[AND toDate(v.date)<=toDate({{date_to}})]] [[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]] [[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]]
), monthly_product_balance AS (
 SELECT toStartOfMonth(date) AS mois, product_id, argMax(solde,tuple(date,stock_move_id)) AS qte_stock
 FROM odoo_analytics.fact_stocks GROUP BY mois,product_id
), monthly_value AS (
 SELECT b.mois,sum(b.qte_stock*p.cout) AS valeur FROM monthly_product_balance b
 INNER JOIN odoo_analytics.dim_produit p ON p.product_id=b.product_id
 WHERE 1=1 [[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]] [[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]] GROUP BY b.mois
)
SELECT round(any(v.cogs)/nullIf(avg(m.valeur),0),2) AS rotation_estimee_proxy
FROM ventes v CROSS JOIN monthly_value m
