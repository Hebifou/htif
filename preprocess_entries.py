import re
from html import unescape

def preprocess_entries(entries: list[dict], mode: str = "auto") -> tuple[list[dict], dict]:
    """
    Bereinigt oder markiert Texte je nach Modus ('auto' oder 'manual').
    Gibt bereinigte Liste und Preprocessing-Statistik zurück.
    """
    cleaned = []
    removed_count = 0
    warnings = 0

    for entry in entries:
        text = entry.get("text", "")
        original = text

        if isinstance(text, str):
            # HTML-Tags entfernen & unescape
            text = unescape(text)
            text = re.sub(r"<[^>]+>", "", text)
            text = text.strip()

        # Entscheidung nach Modus
        if not text:
            if mode == "auto":
                removed_count += 1
                continue  # Ungültig: wird entfernt
            else:
                entry["preprocessing_warning"] = "Leerer oder ungültiger Text"
                warnings += 1

        entry["text"] = text
        cleaned.append(entry)

    stats = {
        "original_total": len(entries),
        "removed_entries": removed_count,
        "warnings_flagged": warnings,
        "final_total": len(cleaned)
    }

    return cleaned, stats
