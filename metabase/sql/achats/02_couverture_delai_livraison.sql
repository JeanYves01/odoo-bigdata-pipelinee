SELECT round(100.0 * countIf(delai_livraison IS NOT NULL) / nullIf(count(), 0), 2) AS couverture_delai_pct
FROM odoo_analytics.fact_achats
