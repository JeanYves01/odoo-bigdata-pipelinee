# Etape 8 - DAGs Airflow

## DAGs
- `extraction_odoo`: quotidien a minuit (Africa/Abidjan), 3 retries / 5 minutes,
  extraction en serie des dix tables depuis `odoo_postgres:5432`, chargement dans
  `clickhouse_dwh:9000`, puis declenchement de `transformation_dbt`.
- `transformation_dbt`: execute dans l'ordre les dossiers staging, intermediate,
  mart, puis `dbt test`. Utilise le venv dbt integre a l'image Airflow.

Tables de reference (partenaires, categories, produits): snapshot complet avec TRUNCATE
et rechargement, donc idempotent. Tables transactionnelles: premiere execution complete,
puis filtre strict `write_date` (commandes/factures) ou `create_date` (lignes, production,
mouvements). Les curseurs sont sauvegardes dans les Airflow Variables uniquement apres
une insertion ClickHouse reussie. Les modeles staging utilisent row_number pour la reprise
sans doublons logiques.

## A propos des faits ReplacingMergeTree
Les marts sont des tables dbt `ReplacingMergeTree()` reconstruites en materialisation `table`.
Les chargements incrementaux concernent la zone Raw; les faits sont recalcules par dbt a
chaque run pour cette simulation de 21 370 lignes. Ne pas presenter ce petit prototype comme
un incremental dbt des faits en production.

## Installation / controle
Les DAGs sont montes depuis `./airflow/dags`. Apres extraction de l'archive, lancer
`docker compose up -d airflow`. Dans l'UI Airflow, activer `extraction_odoo`, puis lancer
`transformation_dbt` manuellement uniquement apres avoir valide les connexions / tables.
La premiere extraction cree les watermarks en Airflow Variables; ne les effacer que si une
reprise complete est volontaire.
