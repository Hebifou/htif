import pandas as pd
import json
from pathlib import Path
from services.analyzer import run_analysis_pipeline

INPUT_PATH = "data/htif_klima_demo_50.csv"
OUTPUT_JSON = "output/htif_results.json"
OUTPUT_CSV = "output/htif_results.csv"
TOPIC = "klima"

def main():
    print("Loading data ...")
    df = pd.read_csv(INPUT_PATH)
    entries = [e for e in df.to_dict(orient="records") if e.get("text")]

    print("Running HTIF analysis pipeline (with Mirror)...")
    result = run_analysis_pipeline(entries, industry=TOPIC, topic=TOPIC)

    Path("output").mkdir(exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    pd.DataFrame(result["data"]).to_csv(OUTPUT_CSV, index=False)

    print("\nResults saved:")
    print(f"- {OUTPUT_JSON}")
    print(f"- {OUTPUT_CSV}")
    print("Done!")

if __name__ == "__main__":
    main()
