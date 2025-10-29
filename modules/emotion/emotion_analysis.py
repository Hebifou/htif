"""
Emotion Analysis Module
-----------------------
Dieses Modul annotiert Einträge mit einer einfachen Emotionserkennung.
Später kannst du hier ein ML-Modell (z. B. HuggingFace) einbauen.
"""

from typing import List, Dict

# --- Dummy-Logik (kann später ersetzt werden) ---
def classify_emotion(text: str) -> str:
    """
    Einfache Regel-basierte Klassifikation.
    Kann später durch ein echtes Modell ersetzt werden.
    """
    text = text.lower()
    if any(word in text for word in ["love", "great", "happy", "good"]):
        return "admiration"
    elif any(word in text for word in ["hate", "bad", "angry", "stupid"]):
        return "anger"
    elif any(word in text for word in ["funny", "lol", "joke"]):
        return "amusement"
    else:
        return "neutral"


def add_emotions_to_entries(entries: List[Dict], **kwargs) -> List[Dict]:
    """
    Fügt jedem Eintrag ein `emotion` Feld hinzu.
    """
    for e in entries:
        text = e.get("text", "")
        e["emotion"] = classify_emotion(text)
    return entries
