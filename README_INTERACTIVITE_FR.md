# Correctif interactif Metabase - Odoo Analytics

Ce lot ajoute des variables de filtre aux 32 questions SQL existantes puis relie les widgets à leurs 4 dashboards existants dans la collection **Odoo Analytics**.

## Filtres proposés
- Tous les dashboards : **Date de début** et **Date de fin** (deux sélecteurs de date, compatibles avec les variables SQL de base de Metabase).
- Tous les dashboards : **Produit (contient)** et **Catégorie (contient)**.
- Ventes : **Client (contient)**.
- Achats : **Fournisseur (contient)**.
- Production : **Statut (contient)**.
- Stocks : **Entrepôt (contient)**.

Les filtres texte sont des champs de recherche libre, pas des listes déroulantes. Les tags sont des variables SQL Metabase optionnelles : sans valeur saisie, elles ne filtrent pas. Les variables date sont séparées début/fin pour rester compatibles et prévisibles sur ces questions natives SQL.

Les questions TRS moyen et couverture de conformité restent sans filtres parce qu'elles renvoient une valeur non mesurable dans ce jeu synthétique. Le correctif ne crée pas de métriques fictives.

## Étape A : installer le lot
Décompressez l'archive à la racine de `C:\odoo-bigdata-pipelinee`, en fusionnant le dossier `metabase` et en ajoutant le script dans `scripts`.

## Étape B : aperçu sans modification
Dans PowerShell :

```powershell
cd C:\odoo-bigdata-pipelinee
.\venv\Scripts\Activate.ps1
python .\scripts\metabase_interactive_upgrade.py
```

Le script demande l'identifiant et le mot de passe Metabase localement, vérifie que les 32 questions et les quatre dashboards sont trouvés, puis affiche un plan. **Sans `--apply`, il n'écrit rien dans Metabase.** Envoyez la sortie du plan pour contrôle.

## Étape C : appliquer après validation du plan
Après confirmation explicite du plan, exécuter :

```powershell
python .\scripts\metabase_interactive_upgrade.py --apply
```

Le script met à jour les SQL des cartes trouvées par titre, crée/actualise les filtres et mappings de dashboard, et conserve les cartes déjà présentes. Si la connexion est interrompue, certaines questions peuvent déjà être mises à jour; relancer en mode aperçu pour vérifier avant toute nouvelle application.

## Après application
Ouvrir chacun des quatre dashboards et vérifier les deux dates, puis essayer un nom partiel de produit, client/fournisseur ou statut selon le dashboard. Contrôler que les cartes concernées changent, que les autres restent cohérentes, et que les indicateurs non mesurables restent présentés comme tels.
