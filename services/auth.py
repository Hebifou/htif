import yaml
from fastapi import HTTPException

API_KEYS_PATH = "config/api_keys.yaml"

def verify_api_key(api_key: str) -> str:
    try:
        with open(API_KEYS_PATH, "r") as f:
            key_data = yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="API-Key-Datei fehlt")

    clients = key_data.get("clients", {})

    for client_name, client_key in clients.items():
        if client_key == api_key:
            return client_name  # Optional: nutzbar für Analyse-Logging etc.

    raise HTTPException(status_code=403, detail="Ungültiger API-Key")
