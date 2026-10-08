-- TRS exige temps planifie, temps d'arret et quantite conforme/rebut.
-- Ces champs ne sont pas simules; renvoyer NULL plutot qu'un KPI invente.
SELECT CAST(NULL AS Nullable(Float64)) AS trs_moyen_non_disponible
