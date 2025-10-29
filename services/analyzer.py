# services/analyzer.py
from services.domain_config import get_modules_for_industry
from modules.registry import ANALYSIS_MODULES, TOPIC_AWARE_MODULES
from modules.mirror.mirror import run_mirror

"""
Analyzer Pipeline – orchestriert die komplette HTIF-Analyse.
------------------------------------------------------------
1️⃣ Lädt die für die Branche relevanten Module
2️⃣ Führt alle Module sequentiell aus (inkl. topic-aware logic)
3️⃣ Integriert abschließend den 🪞 Mirror Layer (Reflexions- & Audit-Schicht)
4️⃣ Gibt ein Gesamtresultat zurück, das direkt im Dashboard nutzbar ist
"""

def run_analysis_pipeline(
    entries: list[dict],
    industry: str,
    topic: str = "klima",
    mode: str = "auto"
) -> dict:
    """
    Führt alle aktiven Analyse-Module für eine Branche aus
    und integriert am Ende automatisch den Mirror-Check.

    Rückgabeformat:
    {
        "data": [...],
        "module_report": {...},
        "mirror_report": {...}
    }
    """

    # === Validierung ===
    if not entries:
        return {
            "data": [],
            "module_report": {"error": "Keine Einträge vorhanden"},
            "mirror_report": {"status": "skipped", "reflections": ["No data to mirror."]}
        }

    modules = get_modules_for_industry(industry)
    module_report = {}

    print(f"\nStarte HTIF-Analysepipeline für '{industry}' – {len(modules)} Module geladen ...\n")

    # === HAUPTANALYSE ===
    for name in modules:
        func = ANALYSIS_MODULES.get(name)
        if not func:
            module_report[name] = "Modul nicht gefunden"
            continue

        try:
            print(f"▶️  Running module: {name}")

            # Topic-aware Module
            if name in TOPIC_AWARE_MODULES:
                entries = func(entries, topic=topic, module_report=module_report)

            # Sonderfall: insights liefert mehrere Rückgabewerte
            elif name == "insights":
                result = func(entries, module_report=module_report)
                if isinstance(result, tuple):
                    entries = result[0]
                    if len(result) > 1 and isinstance(result[1], dict):
                        module_report.update(result[1])
                else:
                    entries = result

            # Standardmodule
            else:
                entries = func(entries, module_report=module_report)

            if name not in module_report:
                module_report[name] = "Erfolgreich"

        except Exception as e:
            module_report[name] = f"⚠Fehler: {str(e)}"
            print(f"Fehler in Modul '{name}': {e}")

    # === Insights sicherstellen ===
    if "insights" not in module_report:
        module_report["insights"] = {}

    print("\n>>>Pipeline Module Report:", module_report)

    # === MIRROR INTEGRATION ===
    print("\nRunning Mirror self-check ...")
    try:
        mirror_report = run_mirror(entries)

        # Spiegel-Metadaten extrahieren
        status = mirror_report.get("status", "ok")
        confidence = mirror_report.get("confidence_level", 1.0)
        anomalies = len(mirror_report.get("anomalies", []))
        reflections = mirror_report.get("reflections", [])

        print(f"Mirror abgeschlossen – Status: {status}, Confidence: {confidence}, Anomalien: {anomalies}")
        if reflections:
            print(f"→ {reflections[0] if reflections else ''}")

    except Exception as e:
        mirror_report = {
            "status": "error",
            "error": str(e),
            "reflections": ["Mirror-Modul konnte nicht ausgeführt werden."]
        }
        print(f"Mirror Error: {e}")

    # === GESAMTERGEBNIS ===
    result = {
        "data": entries,
        "module_report": module_report,
        "mirror_report": mirror_report
    }

    print("\nAnalysepipeline abgeschlossen.")
    print(f"Gesamtresultat: {len(entries)} Einträge analysiert, "
          f"Mirror Confidence {mirror_report.get('confidence_level', 1.0)}\n")

    return result
