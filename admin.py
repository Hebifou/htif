import streamlit as st
import yaml
import uuid
import json
from pathlib import Path
from datetime import datetime

API_KEYS_PATH = Path("config/api_keys.yaml")
LOGS_PATH = Path("output/htif_results.json")  # Beispiel

st.set_page_config("HTIF Admin", layout="wide")
st.title("🔐 HTIF Admin Panel")

# === API-Keys laden ===
if API_KEYS_PATH.exists():
    with open(API_KEYS_PATH, "r") as f:
        api_keys = yaml.safe_load(f)
else:
    api_keys = {}

# === Key-Übersicht ===
st.header("🔑 API-Key Verwaltung")
st.write("Aktive Keys:")

for user, key in api_keys.items():
    st.code(f"{user}: {key}")

# === Key hinzufügen ===
with st.expander("➕ Neuen Key generieren"):
    new_user = st.text_input("Benutzername")
    if st.button("Key erstellen"):
        if new_user:
            new_key = str(uuid.uuid4())
            api_keys[new_user] = new_key
            with open(API_KEYS_PATH, "w") as f:
                yaml.safe_dump(api_keys, f)
            st.success(f"API-Key für {new_user} erstellt.")
            st.code(new_key)
            st.experimental_rerun()
        else:
            st.warning("Benutzername darf nicht leer sein.")

# === Analyse-Log anzeigen ===
st.header("📝 Letzte Analysen")
if LOGS_PATH.exists():
    with open(LOGS_PATH, "r") as f:
        data = json.load(f)

    st.write(f"{len(data.get('data', []))} Einträge gefunden.")
    st.json(data.get("data")[:5])
else:
    st.info("Noch keine Analyse-Logdatei gefunden.")
