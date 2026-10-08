SELECT c.nom AS client, round(sum(f.chiffre_affaires), 2) AS ca
FROM odoo_analytics.fact_ventes AS f
LEFT JOIN odoo_analytics.dim_client AS c ON c.client_id = f.client_id
GROUP BY client_id, client ORDER BY ca DESC LIMIT 10
