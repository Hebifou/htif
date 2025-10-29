from typing import List, Dict, Any, Tuple
import statistics
from datetime import datetime

"""
HTIF Mirror – Reflexions- & Audit-Schicht (Advanced v3)
-------------------------------------------------------
Ziele:
- Konsistenz-Check mit Feldstatistiken & Ausreißererkennung
- ✂️ Scherenlogik: Divergenz zwischen Emotion & Moral quantifizieren
- Shear Index + Confidence Breakdown für das Dashboard
- Menschlich interpretierbare Reflexionen erzeugen
- Rückwärtskompatibel zum alten Report bleiben
"""

# ------------------------------------------------------------
# Konfiguration
# ------------------------------------------------------------
FIELDS_TO_CHECK: Dict[str, Tuple[float, float]] = {
    "emotion_score": (0.0, 1.0),
    "moral_intensity": (0.0, 1.0),
    "toxicity_score": (0.0, 1.0),
    "stance_confidence": (0.0, 1.0),
    "ambivalence_score": (0.0, 1.0),   # erweitert für Dashboard-Kompatibilität
    "resonance_score": (0.0, 1.0),     # erweitert für Meaning Map
}

# ✂️ Scherenlogik-Regeln
SCISSOR_RULES: List[Tuple[str, str, float, float, str, str]] = [
    ("emotion_score", "moral_intensity", 0.7, 0.3, "scissor_emotion_vs_moral",
     "High affect but low moral salience — potential value/emotion divergence."),
    ("emotion_score", "toxicity_score", 0.7, 0.5, "scissor_emotion_plus_toxicity",
     "High affect paired with toxicity — heated discourse pocket."),
    ("moral_intensity", "stance_confidence", 0.6, 0.4, "scissor_moral_vs_stance_conf",
     "Strong moral signal with low stance confidence — classification uncertainty."),
    ("emotion_score", "stance_confidence", 0.6, 0.4, "scissor_emotion_vs_stance_conf",
     "Strong emotional signal with low stance confidence — interpretation ambiguity."),
]

MAX_ANOMALY_EXAMPLES = 100


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _pct(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    n = len(vals)
    i = max(0, min(n - 1, int(round(p * (n - 1)))))
    return float(vals[i])


def _stats(values: List[Any]) -> Dict[str, float]:
    nums = [v for v in values if _is_num(v)]
    if not nums:
        return {"count": 0, "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "p10": 0.0, "p90": 0.0}
    return {
        "count": len(nums),
        "mean": float(statistics.fmean(nums)),
        "std": float(statistics.pstdev(nums)) if len(nums) > 1 else 0.0,
        "min": float(min(nums)),
        "max": float(max(nums)),
        "p10": _pct(nums, 0.10),
        "p90": _pct(nums, 0.90),
    }


def _flag_outliers(values: List[Any], min_val: float, max_val: float, mean: float, std: float, p90: float) -> Dict[str, int]:
    """Zählt Ausreißer pro Feld"""
    out_of_range, z3, above_p90x125 = 0, 0, 0
    for v in values:
        if not _is_num(v):
            continue
        if v < min_val - 1e-9 or v > max_val + 1e-9:
            out_of_range += 1
        if std > 0 and abs((v - mean) / (std + 1e-9)) > 3.0:
            z3 += 1
        if v > (p90 * 1.25):
            above_p90x125 += 1
    return {"out_of_range": out_of_range, "z_score_gt_3": z3, "above_p90x1_25": above_p90x125}


def _apply_scissor_rules(row: Dict[str, Any]) -> List[str]:
    """Gibt ✂️ Flags zurück, falls Divergenzen erkannt werden"""
    flags = []
    for left, right, left_high, right_low, flag_name, _desc in SCISSOR_RULES:
        lv, rv = row.get(left), row.get(right)
        if _is_num(lv) and _is_num(rv) and lv >= left_high and rv <= right_low:
            flags.append(flag_name)
    return flags


# ------------------------------------------------------------
# Hauptfunktion
# ------------------------------------------------------------
def run_mirror(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not entries:
        return {
            "status": "no_data",
            "checked": 0,
            "fields": {},
            "anomalies": [],
            "reflections": ["No entries provided."],
            "confidence_level": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # --- Feldstatistiken ---
    field_reports: Dict[str, Dict[str, Any]] = {}
    total_values = 0
    for field, (fmin, fmax) in FIELDS_TO_CHECK.items():
        vals = [e.get(field) for e in entries if field in e]
        st = _stats(vals)
        out = _flag_outliers(vals, fmin, fmax, st["mean"], st["std"], st["p90"])
        total_values += len(vals)
        field_reports[field] = {**st, **out, "range_min": fmin, "range_max": fmax}

    # --- Entry-Level Checks ---
    anomalies: List[Dict[str, Any]] = []
    total_flag_count = 0
    scissor_total = 0

    for idx, row in enumerate(entries):
        row_flags = []

        for f, (fmin, fmax) in FIELDS_TO_CHECK.items():
            v = row.get(f)
            if not _is_num(v):
                continue
            st = field_reports[f]
            if v < fmin - 1e-9 or v > fmax + 1e-9:
                row_flags.append(f"{f}:out_of_range")
            if st["std"] > 0 and abs((v - st["mean"]) / (st["std"] + 1e-9)) > 3.0:
                row_flags.append(f"{f}:z_score_gt_3")
            if _is_num(st["p90"]) and v > st["p90"] * 1.25:
                row_flags.append(f"{f}:above_p90x1.25")

        scissor_hits = _apply_scissor_rules(row)
        if scissor_hits:
            scissor_total += len(scissor_hits)
        row_flags.extend(scissor_hits)

        if row_flags:
            total_flag_count += len(row_flags)
            row["mirror_flags"] = row_flags
            if len(anomalies) < MAX_ANOMALY_EXAMPLES:
                anomalies.append({
                    "index": idx,
                    "type": ", ".join(row_flags),
                    "text": row.get("text", "")[:500],
                    "values": {f: row.get(f) for f in FIELDS_TO_CHECK.keys()},
                })
        else:
            row["mirror_flags"] = ["ok"]

    checked = len(entries)

    # --- Aggregierte Indizes ---
    shear_index = round(scissor_total / max(checked, 1), 3)
    avg_flags_per_row = total_flag_count / max(checked, 1)
    confidence_level = max(0.0, min(1.0, 1.0 - min(1.0, avg_flags_per_row)))

    # --- Confidence Breakdown ---
    out_of_range_sum = sum(v["out_of_range"] for v in field_reports.values())
    zscore_sum = sum(v["z_score_gt_3"] for v in field_reports.values())
    confidence_breakdown = {
        "range_consistency": round(1 - (out_of_range_sum / max(total_values, 1)), 3),
        "stability": round(1 - (zscore_sum / max(total_values, 1)), 3),
        "moral_emotion_balance": round(1 - shear_index, 3),
    }

    # --- Status ---
    status = "ok"
    if total_flag_count > 0:
        status = "inconsistencies_found"
    if confidence_level < 0.6:
        status = "low_confidence"

    # --- Reflections ---
    reflections = [
        f"{checked} entries checked.",
        f"Total flag count: {total_flag_count}.",
        f"Estimated analysis confidence: {round(confidence_level, 2)}.",
        f"Shear Index (value/moral divergence): {shear_index}.",
    ]
    if confidence_level < 0.5:
        reflections.append("Low analytical confidence — dataset shows fragmented coherence or measurement uncertainty.")
    elif shear_index > 0.3:
        reflections.append("Strong emotional–moral divergence detected — discourse may be polarized or ironic.")
    elif confidence_level > 0.8 and shear_index < 0.1:
        reflections.append("High internal stability — emotional and moral signals appear balanced.")
    else:
        reflections.append("Minor inconsistencies observed, overall coherence maintained.")

    # --- Daten-Anreicherung für Dashboard ---
    for e in entries:
        e["shear_index_local"] = shear_index

    # --- Finaler Report ---
    report: Dict[str, Any] = {
        "status": status,
        "checked": checked,
        "fields": field_reports,
        "anomalies": anomalies,
        "reflections": reflections,
        "confidence_level": round(confidence_level, 3),
        "confidence_breakdown": confidence_breakdown,
        "shear_index": shear_index,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Dashboard-kompatibel: Anzahl markierter Zeilen
    report["flagged_rows"] = len([e for e in entries if e.get("mirror_flags") and e["mirror_flags"] != ["ok"]])

    return report
