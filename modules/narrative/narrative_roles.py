import re
from typing import List, Dict

# Vorab kompilierte Regex-Pattern für Rollenklassifikation
PATTERNS = {
    "held:in": re.compile(r"\b(danke|endlich|mutig|handelt|verantwortung)\b", re.IGNORECASE),
    "opfer": re.compile(r"\b(wir|uns)\b.*\b(zwingen|müssen|verlieren|leiden|bedrohen|verzicht)\b", re.IGNORECASE),
    "gegner": re.compile(r"\b(grüne|politik|regierung|konzerne|die da oben)\b.*\b(zerstören|lügen|schuld)\b", re.IGNORECASE)
}


def classify_narrative_role(text: str) -> str:
    """
    Klassifiziert die Rolle des Sprechers im narrativen Diskurs.
    Rollen: held:in, gegner, opfer, neutral
    """
    if not isinstance(text, str) or not text.strip():
        return "neutral"

    for role, pattern in PATTERNS.items():
        if pattern.search(text):
            return role

    return "neutral"


def add_narrative_roles(entries: List[Dict], **kwargs) -> List[Dict]:
    """
    Fügt jedem Entry eine narrative Rolle hinzu.
    Akzeptiert **kwargs, damit module_report genutzt werden kann.
    """
    module_report = kwargs.get("module_report", {})

    for entry in entries:
        try:
            entry["narrative_role"] = classify_narrative_role(entry.get("text", ""))
        except Exception as e:
            entry["narrative_role"] = "neutral"
            entry["narrative_role_error"] = str(e)

    # Erfolg ins module_report schreiben
    module_report["narrative_roles"] = "Erfolgreich"

    return entries
