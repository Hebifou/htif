import pandas as pd
import emoji
import ftfy
import os
import re
import json

REQUIRED_FIELDS = {"text", "topic_tag", "timestamp", "source", "user_type"}

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')

def clean_text(text):
    text = ftfy.fix_text(text)
    text = remove_emojis(text)
    # Unicode-freundliche Zeichenbereinigung
    text = re.sub(r"[^\w\s.,!?ßäöüÄÖÜ-]", "", text)
    return text.strip()

def transform_row(row):
    return {
        "text": clean_text(row["text"]),
        "topic_tag": row["topic_tag"],
        "timestamp": row["timestamp"],
        "source": row["source"],
        "user_type": row["user_type"]
    }

def preprocess_dataframe(df: pd.DataFrame) -> list[dict]:
    if not REQUIRED_FIELDS.issubset(df.columns):
        missing = REQUIRED_FIELDS - set(df.columns)
        raise ValueError(f"Fehlende Spalten in DataFrame: {missing}")

    # Pandas-optimierte Iteration
    cleaned_rows = df.apply(transform_row, axis=1).tolist()

    if not cleaned_rows:
        raise ValueError("Keine gültigen Zeilen – leeres Ergebnis.")

    return cleaned_rows

def preprocess_csv(input_path: str) -> list[dict]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Eingabedatei nicht gefunden: {input_path}")

    df = pd.read_csv(input_path)
    return preprocess_dataframe(df)

def export_to_json(data: list[dict], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Optional: Standalone CLI
if __name__ == "__main__":
    INPUT_PATH = "data/htif_klima_demo_50.csv"
    OUTPUT_PATH = os.path.abspath("output/htif_prepared_data.json")

    try:
        result = preprocess_csv(INPUT_PATH)
        export_to_json(result, OUTPUT_PATH)
        print(f"{len(result)} Zeilen verarbeitet. Datei gespeichert unter: {OUTPUT_PATH}")
    except Exception as e:
        print("Fehler:", e)
