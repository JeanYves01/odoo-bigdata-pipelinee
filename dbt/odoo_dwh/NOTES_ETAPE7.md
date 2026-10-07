# Etape 7: transformations dbt

## Organisation
- `models/staging`: 10 vues de nettoyage et typage des tables Raw.
- `models/intermediate`: 4 vues enrichies au grain des lignes ou mouvements.
- `models/mart`: 5 dimensions + 4 faits.
- `macros/generate_schema_name.sql`: garde toutes les relations dans la base ClickHouse `odoo_analytics`; les couches sont identifiees par les noms des modeles et leurs dossiers dbt, sans creer des bases ClickHouse distinctes.

## Limites de la simulation a documenter
- La table purchase_order ne contient aucune date de reception effective: `delai_livraison` et le delai moyen fournisseur restent NULL. Ne pas presenter ce KPI comme mesure reelle avant d'ajouter `date_reception` aux donnees.
- La source production n'a pas de temps cible, temps d'arret ni quantite rebut: `trs` reste NULL; le TRS industriel ne peut pas etre calcule honnetement avec ces champs uniquement.
- Les mouvements de stock n'ont pas de `warehouse_id`: une dimension entrepot unique, explicitement simulee (Abidjan), est utilisee. Les donnees ne permettent pas une comparaison entre plusieurs sites.
- Les faits ventes/achats ne retiennent que les commandes confirmees/terminees ou recues, donc leur total de lignes est inferieur au volume source total.
- Les faits utilisent `ReplacingMergeTree()` et sont construits comme des tables dbt pour cette premiere materialisation. L'incrementalite dedoublonnee sera validee lors de l'orchestration et des marqueurs `write_date` de l'etape 8.
