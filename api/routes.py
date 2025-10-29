from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import io
import json
import os
import yaml
import logging
from datetime import datetime

from services.auth import verify_api_key
from services.analyzer import run_analysis_pipeline
from social_api import fetch_instagram_comments, fetch_tiktok_comments

# === Setup ===
router = APIRouter()
EXPORT_DIR = "output/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

API_KEYS_PATH = "config/api_keys.yaml"
ADMIN_SECRET = "SUPERSECRETADMINKEY"  # Optional: aus .env laden

logger = logging.getLogger(__name__)


# === Analyse-Endpunkt ===
@router.post("/analyze")
async def analyze(
    file: UploadFile = File(None),
    topic: str = Form("klima"),
    user_api_key: str = Header(None),
    social_platform: str = Form(None),
    social_id: str = Form(None),
    comment_limit: int = Form(100),
    mode: str = Form("auto")
):
    if not user_api_key:
        raise HTTPException(status_code=400, detail="API-Key erforderlich")

    client_name = verify_api_key(user_api_key)

    if not (file or (social_platform and social_id)):
        raise HTTPException(status_code=400, detail="Datei oder Social-Parameter erforderlich")

    try:
        # === Datenquelle wählen ===
        if social_platform and social_id:
            if social_platform.lower() == "instagram":
                entries = fetch_instagram_comments(social_id, user_api_key, limit=comment_limit)
            elif social_platform.lower() == "tiktok":
                entries = fetch_tiktok_comments(social_id, user_api_key, limit=comment_limit)
            else:
                raise HTTPException(status_code=400, detail="Unbekannte Social Plattform.")
        else:
            content = await file.read()
            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
                entries = df.to_dict(orient="records")
            elif file.filename.endswith(".json"):
                entries = json.loads(content)
            else:
                raise HTTPException(status_code=400, detail="Nur .csv oder .json erlaubt.")

        entries = [e for e in entries if e.get("text")]
        if not entries:
            raise HTTPException(status_code=422, detail="Keine gültigen Texte gefunden.")

        # === Analyse durchführen ===
        analyzed_entries, module_report = run_analysis_pipeline(entries, industry=topic, topic=topic, mode=mode)

        # === Exportpfade vorbereiten ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"htif_result_{timestamp}.csv"
        json_filename = f"htif_result_{timestamp}.json"
        csv_path = os.path.join(EXPORT_DIR, csv_filename)
        json_path = os.path.join(EXPORT_DIR, json_filename)

        # === Export speichern ===
        pd.DataFrame(analyzed_entries).to_csv(csv_path, index=False)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analyzed_entries, f, ensure_ascii=False, indent=2)

        # === Insights extrahieren (falls vorhanden) ===
        insights = module_report.get("insights", {})

        return {
            "message": "Analyse erfolgreich abgeschlossen.",
            "record_count": len(analyzed_entries),
            "csv_url": f"/downloads/{csv_filename}",
            "json_url": f"/downloads/{json_filename}",
            "data": analyzed_entries,  # 👈 volle Daten zurückgeben
            "modules_run": module_report,
            "insights": insights  # 👈 garantiert Dict
        }


    except Exception as e:
        logger.exception("Analysefehler")
        raise HTTPException(status_code=500, detail=f"Analysefehler: {str(e)}")


# === Download-Endpunkt ===
@router.get("/downloads/{filename}")
def download_file(filename: str):
    file_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Datei nicht gefunden.")

    if filename.endswith(".csv"):
        content_type = "text/csv"
    elif filename.endswith(".json"):
        content_type = "application/json"
    else:
        content_type = "application/octet-stream"

    return FileResponse(file_path, media_type=content_type, filename=filename)


# === Admin-API-Key-Check (nicht in OpenAPI-Schema anzeigen) ===
@router.get("/admin/keys", include_in_schema=False)
def list_api_keys(admin_key: str = Header(...)):
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Nicht autorisiert")

    if not os.path.exists(API_KEYS_PATH):
        return {}

    with open(API_KEYS_PATH, "r") as f:
        keys = yaml.safe_load(f)

    return keys
