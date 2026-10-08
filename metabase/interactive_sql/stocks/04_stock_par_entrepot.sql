WITH dernier_solde AS (
 SELECT product_id,argMax(solde,tuple(date,stock_move_id)) AS qte_stock,max(date) AS date
 FROM odoo_analytics.fact_stocks GROUP BY product_id
)
SELECT e.nom AS entrepot,sum(f.qte_stock) AS quantite_stock,round(sum(f.qte_stock*p.cout),2) AS valeur_stock_estimee
FROM dernier_solde f INNER JOIN odoo_analytics.dim_produit p ON p.product_id=f.product_id
CROSS JOIN odoo_analytics.dim_entrepot e WHERE 1=1
[[AND toDate(f.date)>=toDate({{date_from}})]] [[AND toDate(f.date)<=toDate({{date_to}})]] [[AND positionCaseInsensitiveUTF8(p.nom, {{product}}) > 0]] [[AND positionCaseInsensitiveUTF8(p.categorie, {{category}}) > 0]] [[AND positionCaseInsensitiveUTF8(e.nom, {{warehouse}}) > 0]]
GROUP BY e.entrepot_id,entrepot
