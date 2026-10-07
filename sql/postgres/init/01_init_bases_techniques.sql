-- ==================================================================
-- Execute automatiquement au PREMIER demarrage du conteneur PostgreSQL
-- Cree les bases techniques d'Airflow et de Metabase, separees de odoo_db
-- ==================================================================

-- Base de metadonnees Airflow
CREATE USER airflow WITH PASSWORD 'airflow123';
CREATE DATABASE airflow OWNER airflow;

-- Base applicative Metabase (questions, dashboards, utilisateurs)
CREATE USER metabase WITH PASSWORD 'metabase123';
CREATE DATABASE metabase OWNER metabase;
