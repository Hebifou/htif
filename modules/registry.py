# modules/registry.py

# --- Core Analysis Modules ---
from modules.emotion.emotion_analysis import add_emotions_to_entries
from modules.irony.irony_detect import add_irony_labels
from modules.stance.stance_detection import add_stance_to_entries
from modules.framing.framing_detect import add_framing_to_entries
from modules.moral.moral_detect import add_moral_frames
from modules.identity.identity_analysis import add_identity_features
from modules.toxicity.toxicity_detect import add_toxicity_labels
from modules.narrative.narrative_roles import add_narrative_roles
from modules.narrative.narrative_clusters import add_narrative_clusters
from modules.kpi.kpi_calculate import add_kpis_to_entries
from modules.quotes.quote_extraction import add_quotes_to_entries
from modules.insights.insight_generator import add_insights

# --- Mirror (Audit / Reflection Layer) ---
from modules.mirror.mirror import run_mirror


# ============================================================================
# MODULE REGISTRY
# ============================================================================
# Diese Registry verbindet Modulnamen mit den Funktionen, die sie ausführen.
# Sie ermöglicht dynamisches Aktivieren/Deaktivieren einzelner Analysen
# und dient als zentrale Steuerung für die Verarbeitungspipeline.
# ----------------------------------------------------------------------------

ANALYSIS_MODULES = {
    "emotion_analysis": add_emotions_to_entries,
    "irony_detect": add_irony_labels,
    "stance_detection": add_stance_to_entries,
    "framing_detect": add_framing_to_entries,
    "moral_detect": add_moral_frames,
    "identity_analysis": add_identity_features,
    "verbal_aggression_detect": add_toxicity_labels,
    "narrative_roles": add_narrative_roles,
    "narrative_clusters": add_narrative_clusters,
    "kpi_calculate": add_kpis_to_entries,
    "quote_extraction": add_quotes_to_entries,
    "insights": add_insights,

    # 🪞 Der Mirror läuft am Ende zur Reflexion und Prüfung der Analyse-Ergebnisse
    "mirror": run_mirror,
}


# ============================================================================
# TOPIC-AWARE MODULES
# ============================================================================
# Diese Module benötigen zusätzlich ein "topic"-Argument, um kontextabhängig
# zu analysieren (z. B. Themen- oder Diskursbezug).
# ----------------------------------------------------------------------------

TOPIC_AWARE_MODULES = {
    "stance_detection",
    "narrative_clusters",
}
