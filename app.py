import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# === PAGE CONFIG ===
st.set_page_config(page_title="HTIF – How The Internet Feels", layout="wide")

# === DISCLAIMER / HEADER ===
st.markdown("""
<div style='background: linear-gradient(90deg, #000000 0%, #001F3F 100%);
             padding: 1.2rem; border-radius: 12px; color: white; margin-bottom: 1rem;'>
    <h2 style='margin: 0;'>HTIF – How The Internet Feels</h2>
    <p style='margin: 0;'>Mapping the emotional landscape of the internet through AI</p>
</div>

<div style='background-color:#000000; color:#ffffff; padding:10px; border-radius:10px; margin-bottom:15px;'>
⚠️ <b>Prototype Notice:</b> This is a demo version of <b>HTIF (How The Internet Feels)</b>.<br>
No real-time data is collected or stored — all analyses are based on uploaded or sample datasets.
</div>
""", unsafe_allow_html=True)

# === INIT SESSION STATE ===
if "result" not in st.session_state:
    st.session_state["result"] = None

# === MAIN TABS ===
tabs = st.tabs(["Start Analysis", "Results", "Top Quotes", "Mirror Report"])

# === TAB 1: START ANALYSIS ===
with tabs[0]:
    st.header("Input Data")
    st.info("You can upload your dataset or load a demo below. Full analysis (including Mirror) runs directly here.")

    # --- Input Method ---
    input_method = st.radio(
        "Select Input Method:",
        ["Upload File", "API Request", "Social Media Post ID"]
    )

    # --- Shared parameters ---
    api_url = "http://127.0.0.1:8001/analyze"
    domain = st.selectbox("Domain / Topic Area", ["Politics", "Climate", "Music", "Film", "Media", "Finance"])
    mode = st.radio("Select Analysis Mode:", ["Quick (auto-cleaned)", "Pro (manual review)"])
    comment_limit = st.slider("Max Comments to Analyze", 10, 500, 100)
    user_api_key = st.text_input("HTIF API Key", type="password")

    uploaded_file, api_endpoint, post_id, platform = None, None, None, None

    # === INPUT METHOD SECTIONS ===
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload CSV or JSON File", type=["csv", "json"])

    elif input_method == "API Request":
        st.markdown("Retrieve data from an external API (e.g., monitoring or research endpoint).")
        api_endpoint = st.text_input("API Endpoint URL", placeholder="https://api.example.com/comments")
        api_param = st.text_input("Query Parameters (optional)", placeholder="post_id=12345 or topic=climate")

    elif input_method == "Social Media Post ID":
        platform = st.selectbox("Social Media Platform", ["Instagram", "TikTok", "YouTube", "Reddit", "X"])
        post_id = st.text_input("Post or Video ID", placeholder="e.g. 9x1aBcD123")

    # === ANALYSIS START BUTTON ===
    if st.button("Start Full Analysis (with Mirror)"):
        if not user_api_key:
            st.error("Please enter your API key.")
        else:
            try:
                headers = {"user-api-key": user_api_key}
                data = {
                    "topic": domain.lower(),
                    "mode": "auto" if "Quick" in mode else "manual",
                    "comment_limit": str(comment_limit)
                }
                files = {}

                # --- Upload File ---
                if input_method == "Upload File" and uploaded_file:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    with st.spinner("Running full HTIF pipeline..."):
                        response = requests.post(api_url, data=data, files=files, headers=headers)

                # --- API Request ---
                elif input_method == "API Request" and api_endpoint:
                    data.update({"api_endpoint": api_endpoint})
                    if api_param:
                        data.update({"api_param": api_param})
                    with st.spinner("Fetching data from external API..."):
                        response = requests.post(api_url, data=data, headers=headers)

                # --- Social Media Post ---
                elif input_method == "Social Media Post ID" and post_id:
                    data.update({"social_id": post_id, "social_platform": platform})
                    with st.spinner(f"Fetching comments from {platform}..."):
                        response = requests.post(api_url, data=data, headers=headers)

                else:
                    st.warning("Please provide valid input data.")
                    response = None

                # --- Handle Response ---
                if response and response.status_code == 200:
                    result = response.json()
                    st.session_state["result"] = result
                    st.success(f"✅ Full analysis completed successfully (including Mirror check).")
                elif response:
                    st.error(f"API Error {response.status_code}")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.text(response.text)

            except Exception as e:
                st.exception(f"Internal error: {e}")

    # === DEMO DATA ===
    st.markdown("---")
    st.subheader("Load Sample Datasets")

    col1, col2, col3 = st.columns(3)

    def load_demo(path, label, note):
        try:
            with open(path, "r", encoding="utf-8") as f:
                st.session_state["result"] = json.load(f)
            st.success(f"{label} demo loaded successfully.")
            st.info(note)
        except Exception as e:
            st.error(f"{label} demo file not found: {e}")

    with col1:
        if st.button("Trump Discourse"):
            load_demo("htif_demo_trump_20250624_070205.json", "Trump", "Based on social media discourse around Trump (2023).")

    with col2:
        if st.button("Tesla Conversations"):
            load_demo("htif_demo_tesla_20250624_072309.json", "Tesla", "Tweets and comments discussing Tesla and innovation.")

    with col3:
        if st.button("Banking / Inflation"):
            load_demo("final_banking_demo_2024.json", "Banking", "Synthetic comments related to finance and inflation topics.")

# === TAB 2: RESULTS ===
with tabs[1]:
    st.header("Analysis Results")
    result = st.session_state.get("result")

    if result and "data" in result:
        df = pd.DataFrame(result["data"])
        st.subheader("Comment Sample")
        st.dataframe(df.head(), use_container_width=True)

        # --- KPIs ---
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        if "ambivalence_score" in df.columns:
            col1.metric("Avg. Ambivalence", round(df["ambivalence_score"].mean(), 2))
        if "quote_density" in df.columns:
            col2.metric("Avg. Quote Density", round(df["quote_density"].mean(), 2))
        if "resonance_score" in df.columns:
            col3.metric("Avg. Resonance", round(df["resonance_score"].mean(), 2))

        # --- Insights ---
        insights = result.get("insights", {})
        st.subheader("Executive Summary")
        if insights.get("executive_summary"):
            for point in insights["executive_summary"]:
                st.write(f"• {point}")
        else:
            st.info("No executive summary available.")

        st.subheader("Recommended Actions")
        if insights.get("recommended_actions"):
            for action in insights["recommended_actions"]:
                st.write(f"• {action}")
        else:
            st.info("No recommendations available.")
    else:
        st.info("Run or load an analysis to view results.")

# === TAB 3: TOP QUOTES ===
with tabs[2]:
    st.header("Top Quotes by Quote Density")

    if st.session_state.get("result") and "data" in st.session_state["result"]:
        df = pd.DataFrame(st.session_state["result"]["data"])
        if "quote" in df.columns and "quote_density" in df.columns:
            min_density = st.slider("Minimum Quote Density", 0.0, 1.0, 0.3, 0.01)
            filtered = df.dropna(subset=["quote", "quote_density"])
            filtered = filtered[filtered["quote_density"] >= min_density]
            top_quotes = filtered.sort_values(by="quote_density", ascending=False).head(20)

            st.dataframe(top_quotes, use_container_width=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("Export Top Quotes (CSV)",
                               data=top_quotes.to_csv(index=False).encode("utf-8"),
                               file_name=f"htif_top_quotes_{timestamp}.csv",
                               mime="text/csv")
        else:
            st.warning("No quote data available.")
    else:
        st.info("Please load an analysis result first.")

# === TAB 4: MIRROR REPORT ===
with tabs[3]:
    st.header("Mirror Report – Self-Reflection Layer")
    result = st.session_state.get("result")

    if result and "mirror_report" in result:
        mirror = result["mirror_report"]

        st.markdown(f"""
        <div style='background: linear-gradient(90deg, #000000 0%, #001F3F 100%);
                    color: white; padding: 1.2rem; border-radius: 12px; margin-bottom: 1rem;'>
            <b>Entries checked:</b> {mirror.get('checked', 0)}<br>
            <b>Flagged rows:</b> {mirror.get('flagged_rows', 0)}<br>
            <b>Sample size:</b> {mirror.get('sample_size', 0)}<br>
        </div>
        """, unsafe_allow_html=True)

        if mirror.get("flagged_rows", 0) == 0:
            st.success("✅ No anomalies detected — dataset appears consistent and balanced.")
        else:
            st.warning("⚠️ Some anomalies were detected. Review flagged categories below.")
    else:
        st.info("No mirror data available. Upload or run a full pipeline including the mirror module.")

# === FOOTER ===
st.markdown("""
<hr>
<div style='text-align:center; color: #aaa; font-size: 0.9rem;'>
© 2025 <b>How The Internet Feels</b> — Prototype built in minimalist black & white using Streamlit, FastAPI & Hugging Face.
</div>
""", unsafe_allow_html=True)
