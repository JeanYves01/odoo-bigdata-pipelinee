WITH dernier_solde AS (
  SELECT product_id, argMax(solde, tuple(date, stock_move_id)) AS qte_stock
  FROM odoo_analytics.fact_stocks GROUP BY product_id
)
SELECT countIf(qte_stock < 0) AS produits_solde_negatif,
       count() AS produits_avec_mouvements,
       round(100.0 * countIf(qte_stock < 0) / nullIf(count(), 0), 2) AS part_solde_negatif_pct
FROM dernier_solde
