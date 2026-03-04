"""
frontend/app.py
Streamlit UI for Digital Diagnosis 2.0

Pages:
    1. 🏠 Home        — landing page with app info
    2. 🔍 Diagnose    — symptom input + results
    3. 📊 About       — model performance stats

Run from project root:
    streamlit run frontend/app.py
"""

import streamlit as st
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────
API_BASE   = "http://localhost:8000/api"
APP_TITLE  = "Digital Diagnosis 2.0"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        color: #6b7280;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    .prediction-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .rank-badge {
        display: inline-block;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        text-align: center;
        line-height: 32px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
    .severity-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .severity-mild     { background: #d1fae5; color: #065f46; }
    .severity-moderate { background: #fef3c7; color: #92400e; }
    .severity-serious  { background: #fee2e2; color: #991b1b; }
    .severity-critical { background: #fce7f3; color: #9d174d; }
    .disclaimer-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-top: 1.5rem;
    }
    .symptom-tag {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        border: 1px solid #bfdbfe;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.82rem;
        margin: 2px;
    }
    .stat-box {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-box h2 { font-size: 2rem; margin: 0; }
    .stat-box p  { margin: 0; opacity: 0.85; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────

def call_diagnose(symptoms_text: str) -> dict:
    """POST to /api/diagnose and return the JSON response."""
    try:
        resp = requests.post(
            f"{API_BASE}/diagnose",
            json={"symptoms_text": symptoms_text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to the backend. Make sure it is running on port 8000."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The server took too long to respond."}
    except Exception as e:
        return {"error": str(e)}


def get_health() -> dict:
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        return resp.json()
    except Exception:
        return {"status": "unreachable"}


def severity_pill(level: str) -> str:
    return f'<span class="severity-pill severity-{level}">{level}</span>'


def confidence_color(conf: str) -> str:
    return {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(conf, "⚪")


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🩺 Digital Diagnosis 2.0")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Home", "🔍 Diagnose", "📊 About"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API health status
    health = get_health()
    if health.get("status") == "healthy":
        st.success(f"✅ Backend online")
        st.caption(f"Diseases: {health.get('num_diseases', '—')}  |  Symptoms: {health.get('num_symptoms', '—')}")
    else:
        st.error("❌ Backend offline")
        st.caption("Run: `uvicorn backend.main:app --reload`")

    st.markdown("---")
    st.caption("⚠️ For educational purposes only. Not a substitute for professional medical advice.")


# ══════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════════════════
if page == "🏠 Home":

    st.markdown("""
    <div class="main-header">
        <h1>🩺 Digital Diagnosis 2.0</h1>
        <p>AI-powered disease prediction from your symptoms — fast, accurate, and private.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-box"><h2>361</h2><p>Diseases</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-box"><h2>377</h2><p>Symptoms</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-box"><h2>96%</h2><p>Top-3 Accuracy</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-box"><h2>220k</h2><p>Training Samples</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    # How it works
    st.subheader("⚙️ How It Works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 1️⃣ Describe Symptoms")
        st.write("Type your symptoms in plain language — just like you would tell a doctor.")
    with c2:
        st.markdown("#### 2️⃣ AI Analysis")
        st.write("LLM extracts symptoms → LightGBM predicts top-3 diseases → AI generates a summary.")
    with c3:
        st.markdown("#### 3️⃣ Get Results")
        st.write("See top-3 predictions with probabilities, advice, and specialist recommendations.")

    st.markdown("---")

    st.info("👈 Click **🔍 Diagnose** in the sidebar to start.")


# ══════════════════════════════════════════════════════════════════════
# PAGE 2 — DIAGNOSE
# ══════════════════════════════════════════════════════════════════════
elif page == "🔍 Diagnose":

    st.markdown("""
    <div class="main-header">
        <h1>🔍 Symptom Checker</h1>
        <p>Describe your symptoms below and get AI-powered predictions.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Input form ────────────────────────────────────────────────────
    with st.form("diagnose_form"):
        symptoms_text = st.text_area(
            "Describe your symptoms",
            placeholder="e.g. I have had a high fever for 2 days, bad headache, keep coughing and feel very tired. My throat is sore too.",
            height=160,
            max_chars=2000,
            help="Write in plain language. The more detail you provide, the better the prediction.",
        )

        col_l, col_r = st.columns([1, 4])
        with col_l:
            submitted = st.form_submit_button("🔍 Analyse", use_container_width=True, type="primary")
        with col_r:
            st.caption(f"{'✅' if len(symptoms_text) >= 10 else '⚠️'} {len(symptoms_text)} / 2000 characters")

    # ── Process ───────────────────────────────────────────────────────
    if submitted:
        if not symptoms_text.strip():
            st.warning("Please describe your symptoms before submitting.")
        elif len(symptoms_text.strip()) < 10:
            st.warning("Please provide more detail — at least 10 characters.")
        else:
            with st.spinner("🧠 Analysing your symptoms..."):
                result = call_diagnose(symptoms_text)

            # ── Error ─────────────────────────────────────────────────
            if "error" in result:
                st.error(f"❌ {result['error']}")

            # ── Success ───────────────────────────────────────────────
            elif result.get("success"):
                predictions      = result.get("predictions", [])
                matched_symptoms = result.get("matched_symptoms", [])
                summary          = result.get("summary", "")
                proc_ms          = result.get("processing_time_ms", 0)

                st.success(f"✅ Analysis complete in {proc_ms:.0f} ms")

                # ── Matched symptoms ──────────────────────────────────
                if matched_symptoms:
                    st.markdown("#### 🏷️ Identified Symptoms")
                    tags_html = " ".join(f'<span class="symptom-tag">{s}</span>' for s in matched_symptoms)
                    st.markdown(tags_html, unsafe_allow_html=True)
                    st.markdown(f"<br>*{len(matched_symptoms)} symptoms matched from your description.*", unsafe_allow_html=True)

                st.markdown("---")

                # ── Top 3 predictions ─────────────────────────────────
                st.markdown("#### 🎯 Top 3 Predictions")

                for pred in predictions:
                    rank    = pred.get("rank", "—")
                    disease = pred.get("disease", "Unknown").title()
                    prob    = pred.get("probability", 0)
                    conf    = pred.get("confidence", "low")
                    info    = pred.get("info", {})
                    sev     = info.get("severity_level", "moderate")
                    spec    = info.get("specialist_recommendation", "General Practitioner")
                    cat     = info.get("symptom_category", "—")
                    imm_adv = info.get("immediate_advice", [])
                    solutions = info.get("quick_solutions", [])
                    when    = info.get("when_to_seek_help", "")

                    with st.expander(
                        f"{'🥇' if rank==1 else '🥈' if rank==2 else '🥉'} #{rank} — {disease}  |  {prob:.1f}%  {confidence_color(conf)}",
                        expanded=(rank == 1),
                    ):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Probability",  f"{prob:.1f}%")
                        with c2:
                            st.metric("Confidence",   conf.title())
                        with c3:
                            st.metric("Severity",     sev.title())

                        st.markdown(f"**Specialist:** {spec}  &nbsp;|&nbsp;  **Category:** {cat}", unsafe_allow_html=True)
                        st.markdown("---")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("**💊 Immediate Advice**")
                            for a in imm_adv:
                                st.markdown(f"- {a}")
                        with col_b:
                            st.markdown("**🔧 Quick Solutions**")
                            for s in solutions:
                                st.markdown(f"- {s}")

                        if when:
                            st.markdown(f"**🚨 When to Seek Help:** {when}")

                st.markdown("---")

                # ── AI Summary ────────────────────────────────────────
                if summary:
                    st.markdown("#### 🤖 AI Diagnosis Summary")
                    st.info(summary)

                # ── Disclaimer ────────────────────────────────────────
                st.markdown("""
                <div class="disclaimer-box">
                    ⚠️ <strong>Medical Disclaimer:</strong> This is an AI-generated analysis for
                    educational purposes only. It is <strong>not</strong> a substitute for professional
                    medical diagnosis, advice, or treatment. Always consult a qualified healthcare
                    professional for any medical concerns.
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("Something went wrong. Please try again.")


# ══════════════════════════════════════════════════════════════════════
# PAGE 3 — ABOUT
# ══════════════════════════════════════════════════════════════════════
elif page == "📊 About":

    st.markdown("""
    <div class="main-header">
        <h1>📊 About the System</h1>
        <p>Model architecture, performance metrics, and tech stack.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Model performance
    st.subheader("🎯 Model Performance")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Top-1 Accuracy", "85.75%", help="Model picks exact disease correctly")
    with c2:
        st.metric("Top-3 Accuracy", "95.97%", help="True disease is in top-3 predictions")
    with c3:
        st.metric("Top-5 Accuracy", "98.12%", help="True disease is in top-5 predictions")

    st.markdown("---")

    # Pipeline
    st.subheader("⚙️ Pipeline Architecture")
    st.markdown("""
    ```
    Patient Free Text
          │
          ▼
    ┌─────────────────────────────┐
    │  LLM Call #1                │  llama-3.3-70b via Groq
    │  Symptom Extraction         │  Free text → matched symptom list
    └─────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────┐
    │  Binary Vector (377-dim)    │  0/1 per symptom
    └─────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────┐
    │  LightGBM Classifier        │  220k samples | 361 diseases
    │  Top-3 Predictions          │  Disease + probability
    └─────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────┐
    │  Knowledge Base Lookup      │  advice.json enrichment
    └─────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────┐
    │  LLM Call #2                │  llama-3.3-70b via Groq
    │  Diagnosis Summary          │  Patient-friendly explanation
    └─────────────────────────────┘
          │
          ▼
    Final Response to UI
    ```
    """)

    st.markdown("---")

    # Tech stack
    st.subheader("🛠️ Tech Stack")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Backend**
        - FastAPI + Uvicorn
        - LightGBM classifier
        - LangChain + Groq (llama-3.3-70b)
        - Pydantic schemas
        """)
    with col2:
        st.markdown("""
        **Frontend**
        - Streamlit
        - Requests (API calls)

        **Data & Models**
        - 220k patient records
        - 377 binary symptoms
        - 361 disease classes
        """)

    st.markdown("---")
    st.caption("⚠️ Built for educational and research purposes. Not for clinical use.")