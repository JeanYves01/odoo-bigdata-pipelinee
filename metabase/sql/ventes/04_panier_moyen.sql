SELECT round(sum(chiffre_affaires) / nullIf(uniqExact(sale_order_id), 0), 2) AS panier_moyen
FROM odoo_analytics.fact_ventes
