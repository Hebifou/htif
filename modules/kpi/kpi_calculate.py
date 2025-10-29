from typing import Dict, List

# === Basis-KPIs ===

def calculate_quote_density(entry: dict) -> float:
    """
    Verhältnis von Quote-Länge zur Textlänge.
    Je höher, desto prägnanter ist der Beitrag.
    """
    text_len = len(entry.get("text", "").split())
    quote_len = len(entry.get("quote", "").split())

    if text_len == 0:
        return 0.0

    return round(quote_len / text_len, 2)


def calculate_resonance_score(entry: dict) -> float:
    """
    KPI: Quote Density × Ambivalenzscore.
    Gibt Hinweis auf strategische Relevanz.
    """
    qd = entry.get("quote_density", 0.0)
    amb = entry.get("ambivalence_score", 0.0)
    return round(qd * amb, 2)


# === High-End KPIs ===

def calculate_emotion_dominance(entry: dict) -> float:
    """
    Misst, wie dominant die stärkste Emotion im Vergleich zu anderen ist.
    Wertebereich: 0..1 (1 = klar dominiert, 0 = gleichmäßig verteilt).
    """
    scores: Dict[str, float] = entry.get("emotion_scores", {})
    if not scores:
        return 0.0

    top_scores = sorted(scores.values(), reverse=True)[:3]
    if not top_scores or sum(top_scores) == 0:
        return 0.0

    dominance = top_scores[0] / sum(top_scores)
    return round(dominance, 2)


def calculate_valence_shift(entry: dict) -> float:
    """
    Misst das Gleichgewicht zwischen positiven und negativen Emotionen.
    Je näher bei 1.0, desto stärker ist ein Konflikt (gleich stark positiv & negativ).
    Je näher bei 0.0, desto eindeutiger die Valenz.
    """
    vb: Dict[str, float] = entry.get("valence_balance", {})
    pos = vb.get("pos", 0.0)
    neg = vb.get("neg", 0.0)

    if max(pos, neg) == 0:
        return 0.0

    return round(min(pos, neg) / max(pos, neg), 2)


def calculate_conflict_index(entry: dict) -> float:
    """
    Kombination von Resonanzscore und Ambivalenzscore.
    Liefert ein Signal für 'spannungsreiche' Kommentare.
    """
    resonance = entry.get("resonance_score", 0.0)
    amb = entry.get("ambivalence_score", 0.0)
    return round(resonance * amb, 2)


def calculate_strategic_heat(entry: dict) -> float:
    """
    Master-KPI: kombiniert Zitatprägnanz, Ambivalenz und Valenz-Konflikt.
    Je höher, desto strategisch relevanter ist ein Kommentar.
    """
    qd = entry.get("quote_density", 0.0)
    amb = entry.get("ambivalence_score", 0.0)
    vs = calculate_valence_shift(entry)

    return round((qd + amb + vs) / 3, 2)


# === Aggregation in Entries ===

def add_kpis_to_entries(entries: List[dict], **kwargs) -> List[dict]:
    """
    Fügt jedem Eintrag KPIs hinzu.
    Alte + neue High-End-KPIs.
    """
    for entry in entries:
        # Basiswerte absichern
        entry["quote_density"] = calculate_quote_density(entry)
        entry["ambivalence_score"] = entry.get("ambivalence_score", 0.0)

        # KPIs unabhängig von Vorbedingungen berechnen
        entry["resonance_score"] = calculate_resonance_score(entry)
        entry["emotion_dominance"] = calculate_emotion_dominance(entry)
        entry["valence_shift"] = calculate_valence_shift(entry)
        entry["conflict_index"] = calculate_conflict_index(entry)
        entry["strategic_heat"] = calculate_strategic_heat(entry)

    return entries
