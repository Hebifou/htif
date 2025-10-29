# modules/insights/insight_generator.py
from typing import List
import statistics


def add_insights(entries: List[dict], **kwargs) -> List[dict]:
    """
    Generiert Executive Summary & Empfehlungen auf Basis der KPIs
    und hängt sie in den module_report ein.
    """
    module_report = kwargs.get("module_report", {})

    if not entries:
        module_report["insights"] = {
            "executive_summary": ["Keine Daten vorhanden."],
            "recommended_actions": []
        }
        print(">>> INSIGHTS: Keine Daten vorhanden.")
        return entries

    # === KPIs aggregieren ===
    heats = [e.get("strategic_heat", 0) for e in entries if "strategic_heat" in e]
    ambs = [e.get("ambivalence_score", 0) for e in entries if "ambivalence_score" in e]
    pos_shares = [e.get("valence_balance", {}).get("pos", 0) for e in entries]
    neg_shares = [e.get("valence_balance", {}).get("neg", 0) for e in entries]

    avg_heat = round(statistics.mean(heats), 2) if heats else 0
    avg_amb = round(statistics.mean(ambs), 2) if ambs else 0
    avg_pos = round(statistics.mean(pos_shares), 2) if pos_shares else 0
    avg_neg = round(statistics.mean(neg_shares), 2) if neg_shares else 0

    # === Executive Summary ===
    executive_summary = [
        f"Strategic Heat liegt bei {avg_heat}.",
        f"Durchschnittliche Ambivalenz: {avg_amb}.",
        f"Valence Balance: {avg_pos*100:.0f}% positiv, {avg_neg*100:.0f}% negativ."
    ]

    # === Empfehlungen ===
    recommended_actions = []
    if avg_heat > 0.7:
        recommended_actions.append("Thema ist strategisch relevant → sofort ins Krisenboard.")
    if avg_amb > 0.5:
        recommended_actions.append("Ambivalenz hoch → Kommunikationsstrategie differenzieren.")
    if avg_neg > avg_pos:
        recommended_actions.append("Negativität überwiegt → proaktiv positives Narrativ setzen.")
    if not recommended_actions:
        recommended_actions.append("Keine kritischen Signale – Monitoring fortsetzen.")

    # === Insights ins module_report schreiben ===
    module_report["insights"] = {
        "executive_summary": executive_summary,
        "recommended_actions": recommended_actions
    }

    # 👉 Debug-Ausgabe ins Terminal
    print(">>> INSIGHTS BERECHNET:", module_report["insights"])

    return entries
