from typing import List, Dict
import re

# Moral Foundations – deutsche Stichworte
MORAL_FOUNDATIONS = {
    "care": ["schmerz", "leid", "mitgefühl", "schutz", "hilfe", "empathie"],
    "fairness": ["gerecht", "ungerecht", "diskriminierung", "gleich", "fair"],
    "loyalty": ["verrat", "treue", "gemeinschaft", "patriotisch", "uns", "wir"],
    "authority": ["respekt", "gehorsam", "ordnung", "hierarchie", "gesetz"],
    "sanctity": ["rein", "unrein", "schändlich", "heilig", "entweihen", "sünde"]
}

# Kompilierte Regex-Patterns für Performance
COMPILED_MORAL = {
    foundation: [re.compile(rf"\b{re.escape(kw)}\b") for kw in keywords]
    for foundation, keywords in MORAL_FOUNDATIONS.items()
}


def detect_moral_frames(text: str) -> List[str]:
    if not isinstance(text, str) or not text.strip():
        return []

    lowered = text.lower()
    detected = []

    for foundation, patterns in COMPILED_MORAL.items():
        if any(p.search(lowered) for p in patterns):
            detected.append(foundation)

    return detected


def add_moral_frames(entries: List[Dict], **kwargs) -> List[Dict]:
    """
    Fügt jedem Entry moralische Frames hinzu.
    Akzeptiert **kwargs, damit module_report genutzt werden kann.
    """
    module_report = kwargs.get("module_report", {})

    for entry in entries:
        try:
            entry["moral_frames"] = detect_moral_frames(entry.get("text", ""))
        except Exception as e:
            entry["moral_frames"] = []
            entry["moral_error"] = str(e)

    # Erfolg im Report dokumentieren
    module_report["moral_detect"] = "Erfolgreich"

    return entries
