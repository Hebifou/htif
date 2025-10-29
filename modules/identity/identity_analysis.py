import re
from typing import List, Dict

# Sprachmuster (linguistisch)
COLLECTIVE_PATTERNS = [
    r"\bwir\b", r"\buns\b", r"\bunsere[rn]?\b", r"\bgemeinsam\b"
]
ENEMY_PATTERNS = [
    r"\bdie (grünen|regierung|eliten|konzerne|politik)\b",
    r"\bklimadiktatur\b",
    r"\bdie da oben\b"
]

COLLECTIVE_REGEX = [re.compile(p, re.IGNORECASE) for p in COLLECTIVE_PATTERNS]
ENEMY_REGEX = [re.compile(p, re.IGNORECASE) for p in ENEMY_PATTERNS]

def is_valid_text(text: str) -> bool:
    return isinstance(text, str) and text.strip()

def detect_collective_identity(text: str) -> bool:
    if not is_valid_text(text):
        return False
    return bool(re.search(r"\bwir\b|\buns\b|\bunsere\b|\bunser\b", text, re.IGNORECASE))

def detect_enemy_image(text: str) -> bool:
    if not is_valid_text(text):
        return False
    return bool(re.search(r"\bdie da oben\b|\bLobby\b|\bSchuld\b|\bLügen\b|\bSystem\b", text, re.IGNORECASE))

def detect_collective_pattern(text: str) -> bool:
    if not is_valid_text(text):
        return False
    return any(pattern.search(text) for pattern in COLLECTIVE_REGEX)

def detect_enemy_pattern(text: str) -> bool:
    if not is_valid_text(text):
        return False
    return any(pattern.search(text) for pattern in ENEMY_REGEX)

def add_identity_features(entries: List[Dict]) -> List[Dict]:
    for entry in entries:
        try:
            text = entry.get("text", "")
            entry["identity_collective"] = detect_collective_identity(text)
            entry["collective_speech"] = detect_collective_pattern(text)
            entry["identity_enemy"] = detect_enemy_image(text)
            entry["enemy_mention"] = detect_enemy_pattern(text)
        except Exception as e:
            entry["identity_collective"] = False
            entry["collective_speech"] = False
            entry["identity_enemy"] = False
            entry["enemy_mention"] = False
            entry["identity_error"] = str(e)
    return entries
