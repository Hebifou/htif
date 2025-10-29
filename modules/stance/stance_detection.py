from transformers import pipeline
from typing import List, Dict

DEFAULT_HYPOTHESES = {
    "klima": ["Der Text unterstützt Klimaschutz.", "Der Text lehnt Klimaschutz ab."],
    "gender": ["Der Text unterstützt gendergerechte Sprache.", "Der Text lehnt gendergerechte Sprache ab."],
    "politik": ["Der Text unterstützt die Regierung.", "Der Text lehnt die Regierung ab."]
}

_stance_pipeline = None


def get_stance_pipeline():
    global _stance_pipeline
    if _stance_pipeline is None:
        _stance_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _stance_pipeline


def detect_stance(text: str, topic: str = "klima", threshold: float = 0.6) -> Dict[str, str]:
    if not isinstance(text, str) or not text.strip():
        return {"stance": "neutral", "stance_topic": topic}

    hypotheses = DEFAULT_HYPOTHESES.get(topic)
    if not hypotheses:
        return {"stance": "neutral", "stance_topic": topic}

    try:
        classifier = get_stance_pipeline()
        result = classifier(text[:500], candidate_labels=hypotheses, multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))

        if scores[hypotheses[0]] > threshold:
            stance = "for"
        elif scores[hypotheses[1]] > threshold:
            stance = "against"
        else:
            stance = "neutral"

        return {
            "stance": stance,
            "stance_topic": topic,
            "stance_score_for": round(scores[hypotheses[0]], 2),
            "stance_score_against": round(scores[hypotheses[1]], 2)
        }
    except Exception as e:
        return {
            "stance": "neutral",
            "stance_topic": topic,
            "stance_error": str(e)
        }


def add_stance_to_entries(entries: List[Dict], topic: str = "klima", **kwargs) -> List[Dict]:
    """
    Fügt jedem Entry eine Haltungs-Annotation hinzu.
    Akzeptiert **kwargs, damit module_report aus der Pipeline genutzt werden kann.
    """
    module_report = kwargs.get("module_report", {})

    for entry in entries:
        result = detect_stance(entry.get("text", ""), topic=topic)
        entry.update(result)

    # Erfolg im Report markieren
    module_report["stance_detection"] = "Erfolgreich"

    return entries
