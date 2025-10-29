# services/data_fetcher.py
# ============================================================
# HTIF Data Fetcher
# ------------------------------------------------------------
# Zentraler Input-Layer für HTIF:
# - API Requests
# - Social Media Simulation
# - Synthetic Discourse Generator
# ============================================================

import requests
import random


# ------------------------------------------------------------
# API Loader
# ------------------------------------------------------------
def fetch_from_api(api_url: str, api_key: str = None, limit: int = 100) -> list[dict]:
    """
    Lädt Datensätze aus einer externen JSON- oder REST-API.
    Gibt eine Liste von dicts zurück, z. B. [{"text": "..."}].
    """
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    resp = requests.get(api_url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    # Unterstützt sowohl {"data": [...]} als auch reine Listen
    entries = data.get("data", data)
    return entries[:limit]


# ------------------------------------------------------------
# Social Media Simulation
# ------------------------------------------------------------
def fetch_social_media(platform: str, post_id: str, limit: int = 100) -> list[dict]:
    """
    Simuliert Social-Media-Kommentare (Platzhalter bis echte API-Integration).
    Gibt eine Liste von Dictionaries mit Texten zurück.
    """
    return [
        {
            "text": f"Simulated comment {i+1} from {platform} post {post_id}",
            "emotion": random.choice(["joy", "anger", "fear", "trust", "sarcasm"]),
            "stance": random.choice(["supportive", "critical", "neutral"]),
            "ambivalence_score": round(random.uniform(0.1, 0.9), 2),
            "quote_density": round(random.uniform(0.1, 0.9), 2),
            "resonance_score": round(random.uniform(0.1, 0.9), 2),
            "moral_intensity": round(random.uniform(0.1, 0.9), 2),
        }
        for i in range(limit)
    ]


# ------------------------------------------------------------
# Synthetic Discourse Generator
# ------------------------------------------------------------
def generate_synthetic_discourse(topic: str, n: int = 50) -> list[dict]:
    """
    Generiert synthetische Demo-Kommentare mit zufälligen Emotionen, Stances und Scores.
    Kompatibel mit allen Dashboard-Feldern.
    """
    emotions = ["hope", "fear", "anger", "joy", "irony", "trust", "disgust"]
    stances = ["supportive", "critical", "neutral", "ambivalent"]

    data = []
    for i in range(n):
        emo = random.choice(emotions)
        stance = random.choice(stances)
        ambiv = round(random.uniform(0.1, 0.9), 2)
        resonance = round(random.uniform(0.1, 0.9), 2)
        quote_density = round(random.uniform(0.1, 0.9), 2)
        moral_intensity = round(random.uniform(0.1, 0.9), 2)

        text = f"This synthetic comment about {topic} expresses {emo} with a {stance} tone."

        data.append({
            "text": text,
            "emotion": emo,
            "stance": stance,
            "ambivalence_score": ambiv,
            "resonance_score": resonance,
            "quote_density": quote_density,
            "moral_intensity": moral_intensity
        })

    return data


# ------------------------------------------------------------
# Universal Loader Router
# ------------------------------------------------------------
def load_data(input_mode: str, **kwargs) -> list[dict]:
    """
    Vereinheitlicht den Datenzugriff für unterschiedliche Input-Modi.
    Beispiel:
        load_data("api", api_url="https://...", api_key="XYZ")
        load_data("social", platform="tiktok", post_id="12345")
        load_data("synthetic", topic="climate")
    """
    if input_mode == "api":
        return fetch_from_api(kwargs.get("api_url"), kwargs.get("api_key"), kwargs.get("limit", 100))
    elif input_mode == "social":
        return fetch_social_media(kwargs.get("platform"), kwargs.get("post_id"), kwargs.get("limit", 100))
    elif input_mode == "synthetic":
        return generate_synthetic_discourse(kwargs.get("topic", "demo"), kwargs.get("limit", 50))
    else:
        raise ValueError(f"Unknown input_mode: {input_mode}")
