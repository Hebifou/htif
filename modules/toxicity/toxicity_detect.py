from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict

MODEL_NAME = "unitary/toxic-bert"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model = None
_tokenizer = None

def get_toxicity_model():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.to(device)
    return _model, _tokenizer

def detect_toxicity(text: str, threshold: float = 0.5) -> Dict[str, object]:
    if not isinstance(text, str) or not text.strip():
        return {"toxicity_score": None, "is_toxic": False}

    text = text[:512]

    try:
        model, tokenizer = get_toxicity_model()
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            score = torch.sigmoid(outputs.logits)[0][0].item()

        return {
            "toxicity_score": round(score, 3),
            "is_toxic": score > threshold
        }

    except Exception as e:
        return {
            "toxicity_score": None,
            "is_toxic": False,
            "toxicity_error": str(e)
        }

def add_toxicity_labels(data: List[Dict]) -> List[Dict]:
    for entry in data:
        result = detect_toxicity(entry.get("text", ""))
        entry.update(result)
    return data
