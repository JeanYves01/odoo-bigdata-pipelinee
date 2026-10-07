"""Teste l'acces aux 4 services Docker depuis Windows (venv local)."""
import json
import socket
import urllib.request

OK, KO = "[OK]    ", "[ERREUR]"
errors = 0

def test_port(host: str, port: int, name: str, timeout: int = 5) -> bool:
    """Test si un port TCP repond."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:  # noqa: BLE001
        return False

# 1. PostgreSQL
if test_port("localhost", 5432, "PostgreSQL"):
    print(OK, "PostgreSQL 15 : port 5432 repond")
else:
    errors += 1
    print(KO, "PostgreSQL 15 : port 5432 ne repond pas")

# 2. ClickHouse - port natif 9000
if test_port("localhost", 9000, "ClickHouse natif"):
    print(OK, "ClickHouse natif : port 9000 repond")
else:
    errors += 1
    print(KO, "ClickHouse natif : port 9000 ne repond pas")

# 3. ClickHouse - port HTTP 8123
if test_port("localhost", 8123, "ClickHouse HTTP"):
    print(OK, "ClickHouse HTTP : port 8123 repond")
else:
    errors += 1
    print(KO, "ClickHouse HTTP : port 8123 ne repond pas")

# 4. Airflow
if test_port("localhost", 8080, "Airflow"):
    try:
        resp = urllib.request.urlopen("http://localhost:8080/health", timeout=5)
        data = json.loads(resp.read().decode("utf-8"))
        db_status = data.get("metadatabase", {}).get("status", "?")
        sched_status = data.get("scheduler", {}).get("status", "?")
        print(OK, f"Airflow : DB={db_status} | Scheduler={sched_status}")
    except Exception as exc:  # noqa: BLE001
        print(OK, "Airflow : port 8080 repond (details indisponibles)")
else:
    errors += 1
    print(KO, "Airflow : port 8080 ne repond pas")

# 5. Metabase
if test_port("localhost", 3000, "Metabase"):
    try:
        resp = urllib.request.urlopen("http://localhost:3000/api/health", timeout=5)
        print(OK, "Metabase : port 3000 repond et healthcheck OK")
    except Exception:  # noqa: BLE001
        print(OK, "Metabase : port 3000 repond (init en cours...)")
else:
    errors += 1
    print(KO, "Metabase : port 3000 ne repond pas (attends 1-2 min)")

print("-" * 55)
print("RESULTAT :", "TOUS LES PORTS REPONDENT" if errors == 0 else f"{errors} service(s) en erreur")
