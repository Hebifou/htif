# tools/test_modules.py
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from modules.registry import ANALYSIS_MODULES
from services.analyzer import run_analysis_pipeline

# --- Mini-Datensatz zum Testen ---
entries = [
    {"text": "Klima ist wichtig und wir müssen handeln."},
    {"text": "Alles Fake News, man kann denen nicht trauen."},
    {"text": "Danke an die mutigen Menschen, die Verantwortung übernehmen."},
]

industry = "klima"

print(">>> Starte Modultest für Industry:", industry)

# --- Komplette Pipeline laufen lassen ---
entries_out, report = run_analysis_pipeline(entries, industry=industry, topic="klima")

print("\n=== MODULE REPORT ===")
for mod, status in report.items():
    print(f"{mod}: {status}")

print("\n=== SAMPLE ENTRY (erste 2) ===")
for e in entries_out[:2]:
    print(e)

# --- Extra: Insights anzeigen ---
if "insights" in report:
    print("\n=== INSIGHTS ===")
    print(report["insights"])
