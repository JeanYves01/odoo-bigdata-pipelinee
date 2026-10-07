Etape 5 - configuration du projet dbt

- Le projet dbt complet de base est fourni dans dbt/odoo_dwh : ne lance pas dbt init.
- Le profil ClickHouse est dans profiles.yml a cote de dbt_project.yml et cible
  localhost:9000 via le protocole natif, base odoo_analytics, utilisateur default.
- `sources.yml` decrit les tables Raw qui seront creees dans ClickHouse et alimentees
  depuis PostgreSQL par le DAG d'extraction Airflow. dbt-clickhouse ne lit pas directement
  des sources PostgreSQL au moyen d'un `source()` ClickHouse.
- Le mapping de sources est prepare pour les noms `raw_*` de l'etape 6. On ajustera
  ces noms si le DDL Raw adopte une convention differente.
- Le port hote PostgreSQL est 5433 dans ce projet car le 5432 est occupe sur ce PC.
  Cette valeur est utilisee par le generateur Windows; les conteneurs Docker utilisent
  toujours `odoo_postgres:5432` sur le reseau compose.
