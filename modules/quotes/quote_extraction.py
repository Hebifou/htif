import nltk
import re
from nltk.tokenize import sent_tokenize

# Sicherstellen, dass der Punkt-Tokenizer geladen ist
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def extract_quote(text: str) -> str:
    """
    Extrahiert den prägnantesten Satz aus dem Text.
    Falls keine sinnvollen Sätze gefunden werden, wird ein bereinigter Ausschnitt zurückgegeben.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Satzsegmentierung
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    sentences = [s for s in sentences if re.search(r"\w", s)]  # Filtere reine Emojis o. Sonderzeichen

    if not sentences:
        fallback = re.sub(r"[^\w\s.,!?ßäöüÄÖÜ-]", "", text.strip())
        return fallback[:120]

    return max(sentences, key=len)


def add_quotes_to_entries(entries: list[dict], **kwargs) -> list[dict]:
    """
    Fügt jedem Entry ein 'quote'-Feld hinzu.
    Fehler werden im 'quote_error'-Feld dokumentiert.
    Akzeptiert zusätzlich **kwargs, damit es in der Pipeline funktioniert.
    """
    module_report = kwargs.get("module_report", {})

    for entry in entries:
        try:
            text = entry.get("text", "")
            entry["quote"] = extract_quote(text)
        except Exception as e:
            entry["quote"] = ""
            entry["quote_error"] = str(e)

    # Erfolg ins Modul-Report eintragen
    module_report["quote_extraction"] = "Erfolgreich"

    return entries
