import streamlit as st
import json
import pandas as pd
from datetime import datetime
from services.analyzer import run_analysis_pipeline
from services.data_fetcher import (
    fetch_from_api,
    fetch_social_media,
    generate_synthetic_discourse
)
import altair as alt

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="HTIF – How The Internet Feels",
    page_icon="🌐",
    layout="wide"
)

# ===============================
# GLOBAL STYLES (Monochrome Theme)
# ===============================
st.markdown("""
<style>
body { color:#000; background:#fff; }

.htif-header {
  background:#fff;
  padding:1.5rem;
  border-radius:15px;
  box-shadow:0 0 20px rgba(0,0,0,0.05);
  margin-bottom:20px;
}
.htif-title { font-size:2.1rem; font-weight:700; color:#000; }
.htif-subtitle { font-size:1.1rem; color:#333; }

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
  border-bottom:3px solid #000; color:#000 !important;
}
.stTabs [data-baseweb="tab-list"] button { color:#666 !important; }

hr { border:none; height:1px; background:#e5e5e5; margin:1.2rem 0; }

.stSlider [data-baseweb="slider"] .track-1 { background:#000 !important; }
.stSlider [data-baseweb="slider"] [role="slider"] {
  background:#000 !important; border-color:#000 !important;
}
.stRadio [data-baseweb="radio"] input[type="radio"] { accent-color:#000 !important; }

.info-box {
  background:#f9f9f9;
  border:1px solid #dcdcdc;
  color:#333;
  padding:0.9rem 1.1rem;
  border-radius:8px;
  font-weight:600;
}
.info-box-success {
  background:#f8fdf8;
  border:1px solid #b6e2b6;
  color:#2e7d32;
  padding:0.9rem 1.1rem;
  border-radius:8px;
  font-weight:600;
}

.highlight-panel {
  background:#f9f9f9;
  border:1px solid #ddd;
  color:#333;
  padding:0.9rem 1.1rem;
  border-radius:8px;
  font-weight:600;
  margin-bottom:1rem;
}

.glossary-box {
  background:#fafafa;
  border:1px solid #e6e6e6;
  color:#333;
  padding:0.9rem 1.1rem;
  border-radius:10px;
  font-size:0.95rem;
  line-height:1.45rem;
}
.glossary-box b { color:#000; }
</style>

<div class='htif-header'>
  <div class='htif-title'>HTIF – How The Internet Feels</div>
  <div class='htif-subtitle'>Mapping the emotional landscape of the internet through AI</div>
</div>
""", unsafe_allow_html=True)

# ===============================
# PROTOTYPE DISCLAIMER
# ===============================
st.markdown("""
<div style='background:#fff; color:#000; padding:10px; border-radius:10px; margin-bottom:15px;'>
<b>Prototype Notice:</b> Demo version of <b>HTIF</b>. No real-time data collected — analyses are based on uploaded or synthetic datasets.
</div>
""", unsafe_allow_html=True)

# ===============================
# HELPER FUNCTIONS
# ===============================
def render_success_box(message: str):
    st.markdown(f"<div class='info-box-success'>{message}</div>", unsafe_allow_html=True)

def render_info_box(message: str):
    st.markdown(f"<div class='info-box'>{message}</div>", unsafe_allow_html=True)

def render_glossary():
    with st.expander("📘 Glossary — Terms & KPI Scales (0–1)", expanded=False):
        st.markdown("""
<div class='glossary-box'>
<b>Ambivalence Score</b> — contradictory emotions within comments.<br>
<i>Scale:</i> 0 = clear stance, 1 = conflicting emotions.<br><br>

<b>Resonance Score</b> — emotional echo across participants.<br>
<i>Scale:</i> 0 = no echo, 1 = strong emotional ripple.<br><br>

<b>Quote Density</b> — share of quotable or rhetorically sharp statements.<br>
<i>Scale:</i> 0 = neutral comments, 1 = highly quotable discourse.<br><br>

<b>Moral Intensity</b> — strength of ethical or value-based framing.<br>
<i>Scale:</i> 0 = neutral tone, 1 = strong moral stance.<br><br>

<b>Mirror Confidence</b> — internal stability of the analysis.<br>
<i>Scale:</i> 0 = unstable, 1 = consistent.<br><br>

<b>Shear Index</b> — divergence between emotion and moral stance.<br>
<i>Scale:</i> 0 = aligned, 1 = high tension.<br><br>

<b>Toxicity</b> — degree of hostility in language.<br>
<i>Scale:</i> 0 = civil, 1 = offensive or toxic.<br><br>
</div>
""", unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================
if "result" not in st.session_state:
    st.session_state["result"] = None

# ===============================
# TABS
# ===============================
tabs = st.tabs(["Start Analysis", "Results", "Top Quotes", "Mirror Report", "Meaning Map"])

# -------------------------------------------------------------
# TAB 1 – START ANALYSIS
# -------------------------------------------------------------
with tabs[0]:
    st.header("Input Data")
    st.info("Upload a file, connect via API, or generate a synthetic dataset.")

    input_mode = st.radio("Select Input Method:",
        ["Upload File", "API Request", "Social Media Post ID", "Synthetic Dataset"],
        horizontal=True)
    industry = st.selectbox("Domain / Topic Area", ["Politics", "Climate", "Music", "Film", "Media", "Finance"])
    mode = st.radio("Select Analysis Mode:", ["Quick (auto-cleaned)", "Pro (manual review)"], horizontal=True)

    # === Upload File ===
    if input_mode == "Upload File":
        uploaded = st.file_uploader("Upload CSV or JSON File", type=["csv", "json"])
        limit = st.slider("Max Comments to Analyze", 10, 500, 100)
        if uploaded:
            with st.spinner("Running HTIF pipeline..."):
                try:
                    if uploaded.name.endswith(".json"):
                        content = json.load(uploaded)
                        entries = content.get("data", content)[:limit]
                    else:
                        df = pd.read_csv(uploaded).head(limit)
                        entries = df.to_dict(orient="records")
                    st.session_state["result"] = run_analysis_pipeline(entries, industry=industry, topic=industry.lower())
                    render_success_box("Full analysis completed successfully (including Mirror check).")
                except Exception as e:
                    st.error(f"Error: {e}")

    # === API ===
    elif input_mode == "API Request":
        api_key = st.text_input("HTIF API Key", type="password")
        api_url = st.text_input("API Endpoint or Dataset URL")
        limit = st.slider("Max Comments to Retrieve", 10, 500, 100)
        if st.button("Fetch & Analyze via API"):
            if not api_key or not api_url:
                st.warning("Please provide both API Key and URL.")
            else:
                with st.spinner("Fetching via API..."):
                    try:
                        entries = fetch_from_api(api_url, api_key=api_key, limit=limit)
                        st.session_state["result"] = run_analysis_pipeline(entries, industry=industry, topic=industry.lower())
                        render_success_box("Full analysis completed successfully (including Mirror check).")
                    except Exception as e:
                        st.error(f"API error: {e}")

    # === Social Media ===
    elif input_mode == "Social Media Post ID":
        platform = st.selectbox("Platform", ["TikTok", "Instagram", "YouTube", "X (Twitter)"])
        post_id = st.text_input(f"Enter {platform} Post ID")
        limit = st.slider("Max Comments to Fetch", 10, 500, 100)
        if st.button("Fetch & Analyze Comments") and post_id:
            with st.spinner(f"Fetching {limit} comments from {platform}..."):
                try:
                    entries = fetch_social_media(platform, post_id, limit=limit)
                    st.session_state["result"] = run_analysis_pipeline(entries, industry=industry, topic=industry.lower())
                    render_success_box(f"Analysis completed for {platform} post {post_id}.")
                except Exception as e:
                    st.error(f"Error fetching comments: {e}")

    # === Synthetic Dataset ===
    elif input_mode == "Synthetic Dataset":
        limit = st.slider("Number of synthetic comments", 20, 500, 100)
        if st.button("Generate & Analyze"):
            with st.spinner("Generating synthetic discourse..."):
                try:
                    entries = generate_synthetic_discourse(industry, limit)
                    st.session_state["result"] = run_analysis_pipeline(entries, industry=industry, topic=industry.lower())
                    render_success_box("Synthetic dataset analyzed successfully (including Mirror check).")
                except Exception as e:
                    st.error(f"Synthetic generation failed: {e}")

# -------------------------------------------------------------
# TAB 2 – RESULTS
# -------------------------------------------------------------
with tabs[1]:
    st.header("Analysis Results")
    result = st.session_state.get("result")

    if result and "data" in result:
        df = pd.DataFrame(result["data"])
        st.subheader("Comment Sample")
        st.dataframe(df.head(), use_container_width=True)

        st.subheader("Key Metrics")
        c1, c2, c3 = st.columns(3)
        if "ambivalence_score" in df.columns:
            c1.metric("Avg. Ambivalence", round(df["ambivalence_score"].mean(), 2))
        if "quote_density" in df.columns:
            c2.metric("Avg. Quote Density", round(df["quote_density"].mean(), 2))
        if "resonance_score" in df.columns:
            c3.metric("Avg. Resonance", round(df["resonance_score"].mean(), 2))
    else:
        st.info("Run or load an analysis to view results.")
    render_glossary()

# -------------------------------------------------------------
# TAB 3 – TOP QUOTES
# -------------------------------------------------------------
with tabs[2]:
    st.header("Top Quotes by Quote Density")
    if st.session_state.get("result") and "data" in st.session_state["result"]:
        df = pd.DataFrame(st.session_state["result"]["data"])
        if {"quote", "quote_density"} <= set(df.columns):
            min_d = st.slider("Minimum Quote Density", 0.0, 1.0, 0.3, 0.01)
            filt = df.dropna(subset=["quote", "quote_density"])
            filt = filt[filt["quote_density"] >= min_d]
            top_q = filt.sort_values(by="quote_density", ascending=False).head(20)
            st.dataframe(top_q, use_container_width=True)
        else:
            render_info_box("No quote data available.")
    else:
        st.info("Please load an analysis result first.")
    render_glossary()

# -------------------------------------------------------------
# TAB 4 – MIRROR REPORT
# -------------------------------------------------------------
with tabs[3]:
    st.header("Mirror Report — Self-Reflection Layer")
    result = st.session_state.get("result")
    if result and "mirror_report" in result:
        mirror = result["mirror_report"]
        st.markdown(f"<div class='info-box'>Mirror Confidence: {round(mirror.get('confidence_level',0.0),2)}</div>", unsafe_allow_html=True)
        if mirror.get("fields"):
            st.subheader("Field-Level Stats")
            st.dataframe(pd.DataFrame(mirror["fields"]).T, use_container_width=True)
    else:
        st.info("No mirror data available.")
    render_glossary()

# -------------------------------------------------------------
# TAB 5 – MEANING MAP
# -------------------------------------------------------------
with tabs[4]:
    st.header("Meaning Map — Interactive Story Dashboard")
    result = st.session_state.get("result")

    if result and "data" in result:
        df = pd.DataFrame(result["data"]).fillna(0)
        df["emotion_score"] = df.get("emotion_score", df.get("resonance_score", 0))
        df["moral_intensity"] = df.get("moral_intensity", df.get("ambivalence_score", 0))

        mean_emotion = df["emotion_score"].mean()
        mean_moral = df["moral_intensity"].mean()
        mean_amb = df["ambivalence_score"].mean()

        if mean_amb > 0.5:
            mood_text = "Polarized tension — mixed or conflicting emotional states."
        elif mean_emotion > 0.6 and mean_moral < 0.4:
            mood_text = "Expressive but unanchored — emotional debate with low ethical grounding."
        elif mean_moral > 0.6:
            mood_text = "Value-driven reflection — moral reasoning outweighs emotion."
        else:
            mood_text = "Balanced and coherent — emotionally stable discourse."

        st.markdown(f"<div class='highlight-panel'>{mood_text}</div>", unsafe_allow_html=True)

        chart = (
            alt.Chart(df)
            .mark_circle(size=150, opacity=0.8)
            .encode(
                x=alt.X('moral_intensity:Q', title='Moral Intensity (0–1)'),
                y=alt.Y('emotion_score:Q', title='Emotional Charge (0–1)'),
                color=alt.Color('ambivalence_score:Q', scale=alt.Scale(scheme='blues'), title='Ambivalence (0–1)'),
                size=alt.Size('resonance_score:Q', title='Resonance (0–1)'),
                tooltip=['text', 'emotion', 'stance', 'resonance_score', 'ambivalence_score']
            )
            .properties(height=450)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Run a full analysis first to generate the Meaning Map.")
    render_glossary()

# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.markdown("""
<hr>
<div style='text-align:center; color:#aaa; font-size:0.9rem;'>
© 2025 <b>How The Internet Feels</b> — Prototype built with Streamlit, FastAPI & Hugging Face.
</div>
""", unsafe_allow_html=True)
