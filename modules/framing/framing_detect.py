from typing import List
import re
from collections import Counter

# Framing-Kategorien mit Schlüsselwörtern
FRAMING_CATEGORIES = {
    "bedrohung": ["krise", "gefahr", "untergang", "panik", "notstand", "chaos", "bedrohung", "dunkle zeiten"],
    "kampf": ["kampf", "verteidigen", "besiegen", "aufstand", "kämpfen", "gegen", "streiten", "durchsetzen", "konflikt", "sich behaupten"],
    "verlust": ["früher", "verloren", "rückschritt", "vermisst", "abstieg", "verlust", "verloren gegangen"],
    "hoffnung": ["chance", "rettung", "hoffnung", "gemeinsam", "neuanfang", "zukunft", "ermutigend", "schaffen", "verändern", "aufbruch"],
    "schuld": ["schuld", "verantwortlich", "die politik", "die medien", "die da oben", "schuld sind", "vermasselt"]
}

# Kompilierte Regex-Patterns für Performance
COMPILED_FRAMES = {
    frame: [re.compile(rf"\b{re.escape(k)}\b") for k in keywords]
    for frame, keywords in FRAMING_CATEGORIES.items()
}

FRAME_THRESHOLD = 1

def detect_framing(text: str) -> List[str]:
    if not isinstance(text, str) or not text.strip():
        return []

    text_lower = text.lower()
    frame_hits = Counter()

    for frame, patterns in COMPILED_FRAMES.items():
        for pattern in patterns:
            if pattern.search(text_lower):
                frame_hits[frame] += 1

    return [frame for frame, count in frame_hits.items() if count >= FRAME_THRESHOLD]

def add_framing_to_entries(entries: List[dict]) -> List[dict]:
    for entry in entries:
        try:
            entry["framing"] = detect_framing(entry.get("text", ""))
        except Exception as e:
            entry["framing"] = []
            entry["framing_error"] = str(e)
    return entries
