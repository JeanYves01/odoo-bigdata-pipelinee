"""Verification de l'environnement Python du projet odoo-bigdata-pipeline."""
import importlib
import shutil
import subprocess
import sys

PACKAGES = [
    ("dbt.version", "dbt-core"),
    ("dbt.adapters.clickhouse", "dbt-clickhouse"),
    ("psycopg2", "psycopg2-binary"),
    ("clickhouse_driver", "clickhouse-driver"),
    ("clickhouse_connect", "clickhouse-connect"),
    ("sqlalchemy", "sqlalchemy"),
    ("faker", "faker"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("dotenv", "python-dotenv"),
]


def get_version(module_name: str, dist_name: str) -> str:
    try:
        from importlib.metadata import version
        return version(dist_name)
    except Exception:
        mod = importlib.import_module(module_name)
        return getattr(mod, "__version__", "?")


def main() -> int:
    print(f"Python      : {sys.version.split()[0]}")
    print(f"Executable  : {sys.executable}")
    in_venv = sys.prefix != sys.base_prefix
    print(f"Dans le venv: {'OUI' if in_venv else 'NON  <-- active le venv !'}")
    print("-" * 50)

    errors = 0
    for module_name, dist_name in PACKAGES:
        try:
            importlib.import_module(module_name)
            print(f"[OK]     {dist_name:<20} {get_version(module_name, dist_name)}")
        except Exception as exc:  # noqa: BLE001
            errors += 1
            print(f"[ERREUR] {dist_name:<20} {exc}")

    print("-" * 50)
    dbt_path = shutil.which("dbt")
    if dbt_path:
        out = subprocess.run(["dbt", "--version"], capture_output=True, text=True)
        print(out.stdout.strip() or out.stderr.strip())
    else:
        errors += 1
        print("[ERREUR] commande 'dbt' introuvable dans le PATH")

    print("-" * 50)
    if not sys.version.startswith("3.11"):
        errors += 1
        print("[ERREUR] Python 3.11 attendu")
    print("RESULTAT :", "TOUT EST OK" if errors == 0 else f"{errors} probleme(s)")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
