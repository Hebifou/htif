from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict

# Modell laden
MODEL_NAME = "cardiffnlp/twitter-roberta-base-irony"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def detect_irony(text: str, threshold: float = 0.5) -> Dict[str, object]:
    """
    Gibt zurück:
    - is_ironic (bool)
    - irony_score (float)
    """
    if not isinstance(text, str) or not text.strip():
        return {"is_ironic": False, "irony_score": None}

    text = text[:1000]  # Sicherheit bei langen Texten

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding="max_length"
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        irony_score = probs[0][1].item()

    return {
        "is_ironic": irony_score > threshold,
        "irony_score": round(irony_score, 3)
    }


def add_irony_labels(data: List[Dict]) -> List[Dict]:
    """
    Fügt jedem Eintrag is_ironic (bool) & irony_score (float) hinzu.
    """
    for entry in data:
        try:
            result = detect_irony(entry.get("text", ""))
            entry.update(result)
        except Exception as e:
            entry["is_ironic"] = False
            entry["irony_score"] = None
            entry["irony_error"] = str(e)

    return data
