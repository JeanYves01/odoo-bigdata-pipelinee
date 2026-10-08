# Automatiser l'etape 9 Metabase

Le script lit les 32 SQL deja presents dans `metabase/sql/`, cree les questions
et dashboards via l'API Metabase, et les range dans la collection `Odoo Analytics`.
Il reutilise une question existante au nom exact (dont `CA total`) et ne partage
pas le mot de passe: il est demande interactivement et n'est pas ecrit sur disque.

## Lancement sur Windows PowerShell
1. Extraire cette archive a la racine `C:\odoo-bigdata-pipelinee`.
2. Verifier que `metabase\sql\` et `metabase\CATALOGUE.csv` sont deja presents.
3. Dans PowerShell:

```powershell
cd C:\odoo-bigdata-pipelinee
.\venv\Scripts\Activate.ps1
python .\scripts\metabase_bulk_setup.py
```

Puis saisissez votre identifiant et mot de passe Metabase dans la console. Le script cree/reutilise les questions/dashboards par nom. Il utilise l'API locale `http://localhost:3000`.
