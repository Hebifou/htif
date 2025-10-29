import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.analyzer import run_analysis_pipeline

# === Dummy-Daten ===
entries = [
    {"text": "Klima ist wichtig und wir müssen handeln."},
    {"text": "Alles Fake News, man kann denen nicht trauen."},
    {"text": "Ich bin unsicher, ob das wirklich stimmt."}
]

# === Pipeline starten ===
processed, report = run_analysis_pipeline(entries, industry="klima", topic="klima")

print("\n=== MODULE REPORT ===")
for k, v in report.items():
    print(f"{k}: {v}")

print("\n=== INSIGHTS ===")
print(report.get("insights", "⚠️ Keine Insights erzeugt"))

print("\n=== SAMPLE ENTRIES (erste 2) ===")
for e in processed[:2]:
    print(e)

