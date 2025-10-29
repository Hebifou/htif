import os
import sys

# Lokales Projektverzeichnis zum Importpfad hinzufügen (für 'modules', 'services' etc.)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="HTIF API",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS freigeben (für Streamlit oder externe Frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Endpunkte aus api/routes.py einbinden
app.include_router(router)
