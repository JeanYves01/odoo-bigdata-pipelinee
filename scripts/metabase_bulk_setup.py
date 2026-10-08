"""Create the Etape 9 Metabase questions and dashboards in one run.

Reads metabase/CATALOGUE.csv and metabase/sql/{ventes,production,achats,stocks}.
Uses the Metabase API locally; credentials are prompted and never written to disk.
"""
from __future__ import annotations

import csv
import getpass
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MB_URL = os.getenv("METABASE_URL", "http://localhost:3000").rstrip("/")
CATALOGUE = ROOT / "metabase" / "CATALOGUE.csv"
SQL_ROOT = ROOT / "metabase" / "sql"

NAMES = {
    "01_ca_total": "CA total",
    "02_marge_brute": "Marge brute",
    "03_nb_commandes": "Nombre de commandes",
    "04_panier_moyen": "Panier moyen",
    "05_ca_mensuel": "CA mensuel",
    "06_top10_clients": "Top 10 clients",
    "07_ca_par_categorie": "CA par catégorie",
    "08_marge_mensuelle": "Marge mensuelle",
    "01_couverture_trs": "Couverture TRS mesuré",
    "02_trs_moyen_non_disponible": "TRS moyen (non mesurable)",
    "03_ordres_realises_vs_total": "Ordres réalisés vs total",
    "04_duree_moyenne_heures": "Durée moyenne des ordres terminés",
    "05_qte_produite_mensuelle": "Quantité produite par mois",
    "06_production_par_produit": "Production par produit",
    "07_ordres_par_statut": "Ordres par statut",
    "08_duree_mensuelle": "Durée moyenne par mois",
    "01_montant_total": "Montant total des achats",
    "02_couverture_delai_livraison": "Couverture des délais mesurés",
    "03_couverture_conformite": "Couverture de conformité mesurée",
    "04_top10_fournisseurs": "Top 10 fournisseurs",
    "05_montant_mensuel": "Achats par mois",
    "06_montant_par_categorie": "Achats par catégorie",
    "07_commandes_par_statut": "Commandes par statut",
    "08_quantite_par_fournisseur": "Quantité par fournisseur",
    "01_valeur_stock_estimee": "Valeur de stock estimée",
    "02_rotation_estimee": "Rotation estimée (proxy)",
    "03_produits_solde_negatif": "Produits au solde négatif",
    "04_stock_par_entrepot": "Stock par entrepôt",
    "05_mouvements_entrees_sorties": "Mouvements : entrées et sorties",
    "06_top10_valeur_stock": "Top 10 valeur de stock",
    "07_solde_par_produit": "Solde estimé par produit",
    "08_mouvements_mensuels": "Mouvements par mois",
}


def request(path: str, method: str = "GET", payload=None, token: str | None = None):
    url = MB_URL + path
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["X-Metabase-Session"] = token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Impossible de joindre {url}: {exc}") from exc


def normalize_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("data", "results", "items"):
            if isinstance(value.get(key), list):
                return value[key]
    return []


def find_named(endpoint: str, name: str, token: str):
    items = normalize_list(request(endpoint, token=token))
    return next((item for item in items if item.get("name", "").casefold() == name.casefold()), None)


def get_collection(token: str) -> int:
    existing = find_named("/api/collection", "Odoo Analytics", token)
    if existing:
        return existing["id"]
    created = request("/api/collection", "POST", {
        "name": "Odoo Analytics",
        "description": "Questions et tableaux de bord du pipeline analytique Odoo.",
    }, token)
    return created["id"]


def get_database_id(token: str) -> int:
    databases = normalize_list(request("/api/database", token=token))
    for db in databases:
        if db.get("name", "").casefold() == "odoo analytics":
            return db["id"]
    raise RuntimeError("Base Metabase 'Odoo Analytics' introuvable. Vérifie sa connexion avant le script.")


def display_for(viz: str) -> str:
    return {"Number": "scalar", "Bar": "bar", "Line": "line", "Donut": "pie"}.get(viz, "table")


def catalogue_rows():
    with CATALOGUE.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def card_search(name: str, token: str):
    query = urllib.parse.urlencode({"query": name, "models": "card"})
    result = request("/api/search?" + query, token=token)
    items = normalize_list(result)
    for item in items:
        if item.get("name", "").casefold() == name.casefold() and item.get("model") in ("card", "dataset", None):
            return item
    return None


def create_or_reuse_card(row, database_id: int, collection_id: int, token: str):
    question_ref = row["Question"]
    sql_path = SQL_ROOT / (question_ref + ".sql")
    if not sql_path.is_file():
        raise RuntimeError(f"Fichier SQL manquant: {sql_path}")
    slug = sql_path.stem
    title = NAMES.get(slug, re.sub(r"^\d+_", "", slug).replace("_", " ").title())
    existing = card_search(title, token)
    if existing:
        print(f"  Réutilisée : {title}")
        return existing["id"], title
    sql = sql_path.read_text(encoding="utf-8-sig").strip().rstrip(";") + ";"
    body = {
        "name": title,
        "description": row.get("Description", ""),
        "collection_id": collection_id,
        "display": display_for(row.get("Visualisation", "Table")),
        "visualization_settings": {},
        "dataset_query": {
            "type": "native",
            "database": database_id,
            "native": {"query": sql},
        },
    }
    card = request("/api/card", "POST", body, token)
    print(f"  Créée    : {title}")
    return card["id"], title


def dashboard_cards(detail: dict) -> list[dict]:
    raw = detail.get("dashcards") or detail.get("ordered_cards") or []
    result = []
    for item in raw:
        card_id = item.get("card_id")
        if card_id is None and isinstance(item.get("card"), dict):
            card_id = item["card"].get("id")
        if card_id is None:
            continue
        result.append({
            "id": item.get("id", -1 - len(result)),
            "card_id": card_id,
            "row": item.get("row", 0),
            "col": item.get("col", 0),
            "size_x": item.get("size_x", 6),
            "size_y": item.get("size_y", 4),
            "parameter_mappings": item.get("parameter_mappings", []),
            "series": item.get("series", []),
            "visualization_settings": item.get("visualization_settings", {}),
        })
    return result


def create_dashboard(name: str, collection_id: int, token: str) -> dict:
    found = find_named("/api/dashboard", name, token)
    if found:
        print(f"Tableau réutilisé : {name}")
        return request(f"/api/dashboard/{found['id']}", token=token)
    created = request("/api/dashboard", "POST", {
        "name": name,
        "description": f"Indicateurs analytiques Odoo : {name}.",
        "collection_id": collection_id,
        "parameters": [],
    }, token)
    print(f"Tableau créé : {name}")
    return created


def add_cards_to_dashboard(dashboard: dict, cards: list[tuple[int, str]], token: str):
    dashboard_id = dashboard["id"]
    detail = request(f"/api/dashboard/{dashboard_id}", token=token)
    payload_cards = dashboard_cards(detail)
    have = {card["card_id"] for card in payload_cards}
    missing = [c for c in cards if c[0] not in have]
    if not missing:
        print(f"  Cartes déjà présentes : {dashboard.get('name', dashboard_id)}")
        return
    for card_id, _title in missing:
        idx = len(payload_cards)
        payload_cards.append({
            "id": -1 - idx,
            "card_id": card_id,
            "row": (idx // 2) * 4,
            "col": (idx % 2) * 6,
            "size_x": 6,
            "size_y": 4,
            "parameter_mappings": [],
            "series": [],
            "visualization_settings": {},
        })
    body = {"cards": payload_cards}
    if detail.get("tabs") is not None:
        body["tabs"] = detail["tabs"]
    try:
        request(f"/api/dashboard/{dashboard_id}/cards", "PUT", body, token)
    except RuntimeError as exc:
        raise RuntimeError(
            f"Ajout groupé des cartes impossible sur le dashboard '{dashboard.get('name')}'. "
            "Les questions déjà créées sont conservées; ne relance pas le script avant de vérifier le dashboard. " + str(exc)
        ) from exc
    print(f"  Ajoutées {len(missing)} carte(s) au tableau : {dashboard.get('name', dashboard_id)}")


def main():
    if not CATALOGUE.is_file():
        raise RuntimeError(f"Catalogue introuvable: {CATALOGUE}; décompresse d'abord le zip de l'étape 9 à la racine.")
    username = input("Email / identifiant Metabase : ").strip()
    password = getpass.getpass("Mot de passe Metabase (saisi localement, non sauvegardé) : ")
    session = request("/api/session", "POST", {"username": username, "password": password})
    token = session.get("id")
    if not token:
        raise RuntimeError("Metabase n'a pas retourné de session valide.")
    try:
        collection_id = get_collection(token)
        database_id = get_database_id(token)
        rows = catalogue_rows()
        groups: dict[str, list[tuple[int, str]]] = {}
        for row in rows:
            dashboard_name = row["Dashboard"].strip()
            card_id, title = create_or_reuse_card(row, database_id, collection_id, token)
            groups.setdefault(dashboard_name, []).append((card_id, title))
        print("\nRattachement aux dashboards...")
        for dashboard_name, cards in groups.items():
            dashboard = create_dashboard(dashboard_name, collection_id, token)
            add_cards_to_dashboard(dashboard, cards, token)
        print(f"\nTerminé : {len(rows)} questions traitées et {len(groups)} dashboards vérifiés.")
        print("Ouvre la collection 'Odoo Analytics' dans Metabase pour les consulter.")
    finally:
        try:
            request("/api/session", "DELETE", {}, token)
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERREUR: {exc}", file=sys.stderr)
        raise SystemExit(1)
