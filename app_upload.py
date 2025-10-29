import streamlit as st
import pandas as pd
import json

from modules import add_quotes_to_entries
from modules.emotion.emotion_analysis import add_emotions_to_entries
from kpi_calculate import add_kpis_to_entries
from modules.narrative.narrative_roles import add_narrative_roles
from modules.framing.framing_detect import add_framing_to_entries
from modules.irony.irony_detect import add_irony_labels

st.set_page_config(page_title="HTIF Upload", layout="centered")
st.title("HTIF – Eigene Textdaten analysieren")

st.markdown("""
Laden Sie eine eigene Datei im CSV- oder Excel-Format hoch.  
**Mindestanforderung:** Eine Spalte mit dem Namen `text` oder ein gleichwertiges Feld (`review`, `comment`, `message`...).

Das System erkennt automatisch **Zitate, Emotionen, narrative Rollen, Framing** und mehr.
""")

uploaded_file = st.file_uploader("📂 Datei hochladen", type=["csv", "xlsx"])

if uploaded_file:
    st.success(f"Datei geladen: {uploaded_file.name}")

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Automatische Umbenennung alternativer Spalten
        synonyms = ["review", "comment", "message", "content"]
        if "text" not in df.columns:
            for alt in synonyms:
                if alt in df.columns:
                    df.rename(columns={alt: "text"}, inplace=True)
                    st.info(f"Spalte '{alt}' wurde automatisch zu 'text' umbenannt.")
                    break

        if "text" not in df.columns:
            st.error("Die Datei muss eine Spalte namens `text` enthalten.")
            st.stop()

        #Nur die ersten 100 Zeilen für schnelles Testing
        df = df.sample(min(len(df), 100), random_state=42)

        st.markdown("### Vorschau der hochgeladenen Datei:")
        st.dataframe(df[["text"]].head())

        if st.button("Analyse starten"):
            entries = df.to_dict(orient="records")
            total = len(entries)
            progress = st.progress(0, text="Starte Analyse...")

            # Pipeline mit Fortschrittsbalken
            for i, entry in enumerate(entries):
                entry = add_quotes_to_entries([entry])[0]
                entry = add_emotions_to_entries([entry])[0]
                entry = add_kpis_to_entries([entry])[0]
                entry = add_narrative_roles([entry])[0]
                entry = add_framing_to_entries([entry])[0]
                entry = add_irony_labels([entry])[0]

                entries[i] = entry
                progress.progress((i + 1) / total, text=f"Verarbeite Beitrag {i + 1} von {total}...")

            progress.empty()
            st.success("Analyse abgeschlossen.")

            # Ergebnisse speichern
            output_path = "output/htif_enriched_data.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

            # Ergebnisvorschau
            st.markdown("### Vorschau der Ergebnisse:")
            preview_df = pd.DataFrame(entries[:5])
            st.dataframe(preview_df[["text", "framing", "narrative_role", "ambivalence_score", "is_ironic"]])

            # CSV-Download
            result_df = pd.DataFrame(entries)
            csv_data = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("Ergebnisse als CSV herunterladen", csv_data, "htif_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Fehler beim Einlesen oder Analysieren: {e}")
