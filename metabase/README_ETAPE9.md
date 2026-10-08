# Etape 9 - Dashboards Metabase sur ClickHouse

## Connexion
Dans Metabase: Admin > Databases > Add database > ClickHouse.
- Display name: Odoo Analytics
- Host: clickhouse_dwh (si Metabase est dans le compose `pipeline_net`)
- Port: 8123 (HTTP)
- Database: odoo_analytics
- Username: default
- Password: laisser vide
- Secure/SSL: desactive
Le driver ClickHouse est integre aux versions Metabase 54+; ne pas installer de JAR externe.

## Construire chaque question
Pour chaque fichier SQL du dossier `sql`, creer une nouvelle question > Native query > choisir Odoo Analytics, coller le SQL, executer, puis sauvegarder avec le nom du fichier (sans `.sql`). Choisir le type de visualisation indique dans `CATALOGUE.csv`, puis ajouter la question au dashboard correspondant. Recommander la collection `Reporting Odoo`.
Les requetes SQL de cette archive sont des questions de lecture seule. Elles s'appuient sur les tables/vues `odoo_analytics` construites a l'etape 7. Ne pas creer de question avant que les modeles dbt soient presents.

## Limites analytiques a afficher dans le memoire
- TRS: le jeu de donnees ne comporte ni temps de production planifie, ni arrets, ni rebuts. Le TRS n'est pas calculable. Les cartes Production 01 et 02 montrent la couverture de mesure (0%), pas un TRS.
- Delai d'achat et conformite de livraison: pas de date de reception ni date promise. Les cartes Achats 02/03 montrent la couverture de mesure (0%), pas une performance fournisseur.
- Entrepot: les mouvements sources ne portent pas d'identifiant de site. Un seul entrepot simule est expose; ne pas conclure sur une repartition multi-sites.
- Rupture: aucune demande non servie ni snapshot journalier des stocks. La carte Stocks 03 mesure les produits a solde negatif, indicateur d'anomalie/proxy, pas un taux de rupture observe.
- Rotation de stock: estimation COGS / moyenne des valorisations de fin de mois ou des mouvements observes; voir commentaires dans la requete, ce n'est pas une mesure d'inventaire mensuel complet.

## Rafraichissement / securite
Metabase lance les SELECT directement sur ClickHouse; ces cartes ne copient pas de donnees. Avec le compte `default` sans mot de passe, garder l'instance exposee uniquement sur la machine locale pour ce projet. Ne pas publier les ports ou l'interface sur Internet.
