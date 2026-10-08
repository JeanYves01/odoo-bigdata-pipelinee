SELECT round(100.0 * countIf(trs IS NOT NULL) / nullIf(count(), 0), 2) AS couverture_trs_pct
FROM odoo_analytics.fact_production
