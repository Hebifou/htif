import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="HTIF Analyse", layout="wide")

# === Prototype Disclaimer ===
st.markdown(
    """
    <div style='background-color:#fff3cd; padding:10px; border-radius:10px; margin-bottom:15px;'>
        ⚠️ <b>Prototype Notice:</b> This Streamlit app is an experimental demo of <b>HTIF (How The Internet Feels)</b>.<br>
        It does not collect or store any live user data. All analyses are based on sample or uploaded datasets.
    </div>
    """,
    unsafe_allow_html=True
)

# === Session State initialisieren ===
if "result" not in st.session_state:
    st.session_state["result"] = None


# === Tabs definieren ===
tabs = st.tabs(["Analyse starten", "Ergebnisse", "Top-Zitate"])

# === TAB 1: ANALYSE STARTEN ===
with tabs[0]:
    st.title("HTIF Social Media Analyse")
    st.header("1. Eingabe")

    api_url = "http://127.0.0.1:8001/analyze"

    industry = st.selectbox("Branche / Themenbereich", ["politik", "klima", "musik", "film", "media", "finance"])
    mode = st.radio("Analysemodus wählen:", ["Schnell (automatisch bereinigen)", "Pro (manuell prüfen)"])
    platform = st.selectbox("Social Media Plattform", ["", "instagram", "tiktok"])
    post_id = st.text_input("Post- oder Video-ID")
    comment_limit = st.slider("Max. Kommentare", 10, 500, 100)
    uploaded_file = st.file_uploader("Alternativ: CSV oder JSON Datei hochladen")
    user_api_key = st.text_input("HTIF API-Key", type="password")

    if st.button("Analyse starten"):
        if not user_api_key:
            st.error("Bitte API-Key eingeben.")
        elif not (uploaded_file or (platform and post_id)):
            st.error("Bitte Datei hochladen oder Social-Media-Daten eingeben.")
        else:
            try:
                data = {
                    "topic": industry,
                    "social_platform": platform,
                    "social_id": post_id,
                    "comment_limit": str(comment_limit),
                    "mode": "auto" if "Schnell" in mode else "manual"
                }
                headers = {"user-api-key": user_api_key}
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())} if uploaded_file else {}

                with st.spinner("Analysiere Kommentare..."):
                    response = requests.post(api_url, data=data, files=files, headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    st.session_state["result"] = result
                    st.success(f"{result['record_count']} Kommentare verarbeitet.")
                else:
                    st.error(f"Fehler {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.exception(f"Interner Fehler: {e}")

    st.markdown("---")
    with st.expander("Beispiel-Demos laden"):
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Trump-Diskurs laden"):
                try:
                    with open("htif_demo_trump_20250624_070205.json", "r", encoding="utf-8") as f:
                        st.session_state["result"] = json.load(f)
                    st.success("Trump-Demodaten erfolgreich geladen.")
                except Exception:
                    st.error("Trump-Demo-Datei nicht gefunden.")

        with col2:
            if st.button("Tesla-Diskurs laden"):
                try:
                    with open("htif_demo_tesla_20250624_072309.json", "r", encoding="utf-8") as f:
                        st.session_state["result"] = json.load(f)
                    st.success("Tesla-Demodaten erfolgreich geladen.")
                except Exception:
                    st.error("Tesla-Demo-Datei nicht gefunden.")

        with col3:
            if st.button("Bankendiskurs laden"):
                try:
                    with open("final_banking_demo_2024.json", "r", encoding="utf-8") as f:
                        st.session_state["result"] = json.load(f)
                    st.success("Bankendiskurs-Demodaten erfolgreich geladen.")
                    st.info("Analyse basiert auf synthetischen Kommentaren zu Inflation & Banken.")
                except Exception:
                    st.error("Banken-Demo-Datei nicht gefunden.")

# === TAB 2: ERGEBNISSE ===
with tabs[1]:
    result = st.session_state.get("result")
    st.title("Analyseergebnisse")

    if result:
        df = pd.DataFrame(result["data"])
        st.subheader("Kommentare (Auszug)")
        st.dataframe(df.head(), use_container_width=True)

        if "preprocessing" in result:
            st.subheader("Preprocessing")
            st.json(result["preprocessing"])

        if "modules_run" in result:
            st.subheader("Analyse-Module")
            for mod, status in result["modules_run"].items():
                st.write(f"• `{mod}` → {status}")

        if "csv_url" in result:
            st.markdown(f"📄 [Kommentare als CSV exportieren]({result['csv_url']})")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_bytes = json.dumps(result, indent=2).encode("utf-8")
        st.download_button("📥 Download JSON mit Zeitstempel",
                           data=json_bytes,
                           file_name=f"htif_result_{timestamp}.json",
                           mime="application/json")

        st.subheader("KPIs")
        if "ambivalence_score" in df.columns:
            st.metric("Ø Ambivalenz", round(df["ambivalence_score"].mean(), 2))
        if "quote_density" in df.columns:
            st.metric("Ø Quote Density", round(df["quote_density"].mean(), 2))
        if "resonance_score" in df.columns:
            st.metric("Ø Resonanz", round(df["resonance_score"].mean(), 2))

        # === Insights ===
        insights = result.get("insights", {})

        st.subheader("📊 Executive Summary")
        if insights.get("executive_summary"):
            for point in insights["executive_summary"]:
                st.write(f"- {point}")
        else:
            st.info("Keine Executive Summary verfügbar.")

        st.subheader("✅ Handlungsempfehlungen")
        if insights.get("recommended_actions"):
            for action in insights["recommended_actions"]:
                st.write(f"- {action}")
        else:
            st.info("Keine Empfehlungen verfügbar.")

    else:
        st.info("Noch keine Analyse durchgeführt.")

# === TAB 3: TOP-ZITATE ===
with tabs[2]:
    st.title("Top-Zitate (nach Quote Density)")

    if st.session_state.get("result"):
        df = pd.DataFrame(st.session_state["result"]["data"])

        if "quote" in df.columns and "quote_density" in df.columns:
            st.subheader("Top-Zitate filtern")
            min_density = st.slider("Minimaler Quote Density", 0.0, 1.0, 0.3, 0.01)

            filtered = df[["quote", "quote_density"]].dropna()
            filtered = filtered[filtered["quote_density"] >= min_density]
            top_quotes = filtered.sort_values(by="quote_density", ascending=False).head(20)

            st.dataframe(top_quotes, use_container_width=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("Export Top-Zitate (CSV)",
                               data=top_quotes.to_csv(index=False).encode("utf-8"),
                               file_name=f"htif_top_quotes_{timestamp}.csv",
                               mime="text/csv")
        else:
            st.warning("Keine Zitatdaten verfügbar.")
    else:
        st.info("Bitte zuerst eine Analyse durchführen.")
