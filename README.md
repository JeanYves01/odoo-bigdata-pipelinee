# Pipeline Big Data pour le Reporting Analytique Odoo

Projet de mémoire de **Master 2 Mobiquité, Big Data et Systèmes** (ESATIC, Abidjan, Côte d'Ivoire).
Stage réalisé chez **PROGISTACK**, intégrateur Odoo, en tant que Business Analyst Odoo.

## Problématique

> Comment concevoir un pipeline Big Data moderne permettant de transformer les données
> opérationnelles d'un ERP (cas d'Odoo) en insights analytiques actionnables pour les
> décideurs d'une entreprise industrielle ?

## Architecture

```
PostgreSQL 15 (base Odoo simulée)
        │  Extract
        ▼
Apache Airflow 2.9 (orchestration)
        │  Load
        ▼
ClickHouse (Data Warehouse : zone Raw)
        │  Transform : dbt-core + dbt-clickhouse
        ▼     staging → intermediate → mart
ClickHouse (schéma en étoile : dimensions + faits)
        │
        ▼
Metabase (dashboards KPIs : Ventes, Production, Achats, Stocks)
```

Tous les services tournent sous **Docker Desktop**. dbt est développé en local dans un environnement virtuel Python 3.11.

## Stack technique

| Composant      | Rôle                                  | Accès                          |
|----------------|---------------------------------------|--------------------------------|
| PostgreSQL 15  | Source de données (simulation Odoo)   | `localhost:5432`               |
| Airflow 2.9    | Orchestration des flux ELT            | http://localhost:8080          |
| ClickHouse     | Data Warehouse analytique             | http://localhost:8123/play     |
| dbt-core       | Transformations SQL et tests qualité  | CLI (venv)                     |
| Metabase       | Visualisation / self-service BI       | http://localhost:3000          |

## Structure du projet

```
odoo-bigdata-pipeline/
├── airflow/
│   ├── dags/            # DAGs extraction_odoo et transformation_dbt
│   ├── logs/
│   └── plugins/
├── dbt/                 # Projet dbt odoo_dwh (staging, intermediate, mart)
├── scripts/             # generate_data.py (données fictives Odoo)
├── sql/clickhouse/      # Scripts DDL ClickHouse
├── data/                # Données générées (non versionnées)
├── docs/                # Captures et documentation du mémoire
├── docker-compose.yml
└── README.md
```

## Modèle analytique (schéma en étoile)

- **Faits** : `fact_ventes`, `fact_achats`, `fact_production`, `fact_stocks`
- **Dimensions** : `dim_produit`, `dim_client`, `dim_fournisseur`, `dim_temps`, `dim_entrepot`

## Données simulées

21 370 enregistrements répartis sur 10 tables Odoo (`res_partner`, `product_template`,
`product_category`, `sale_order`, `sale_order_line`, `purchase_order`, `purchase_order_line`,
`mrp_production`, `stock_move`, `account_move`), sur la période janvier 2024 à décembre 2025.

## Installation

> Section complétée au fil des étapes du projet.

## Avancement

- [x] Étape 0 : Prérequis système
- [x] Étape 1 : Structure du projet et GitHub
- [ ] Étape 2 : Environnement virtuel Python
- [ ] Étape 3 : Infrastructure Docker
- [ ] Étape 4 : Génération des données
- [ ] Étape 5 : Configuration dbt
- [ ] Étape 6 : Tables ClickHouse
- [ ] Étape 7 : Modèles dbt
- [ ] Étape 8 : DAGs Airflow
- [ ] Étape 9 : Dashboards Metabase
- [ ] Étape 10 : Tests et validation

## Auteur

**Jean Vianney** : Master 2 Mobiquité, Big Data et Systèmes, ESATIC
