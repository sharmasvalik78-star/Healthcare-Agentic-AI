from __future__ import annotations

import os
from typing import Any, Iterable, Optional

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from agents.diet_agent import run_diet_agent
from agents.medicine_agent import run_medicine_agent
from agents.report_agent import run_report_agent
from agents.symptom_agent import run_symptom_agent

# =========================
# PAGE CONFIG
# =========================

load_dotenv()

st.set_page_config(
    page_title="Agentic AI Healthcare Assistant",
    page_icon="🩷",
    layout="wide",
)

# =========================
# CUSTOM CSS
# =========================

st.markdown(
    """
<style>
.main { background-color: #0E1117; color: white; }
.stButton>button { border-radius: 10px; height: 50px; font-size: 18px; font-weight: bold; }
h1, h2, h3 { color: #4CAF50; }
.block-container { padding-top: 2rem; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================


def _safe_get(obj: Any, attr: str, default: Any) -> Any:
    return getattr(obj, attr, default) if obj is not None else default


def _render_bullets(items: Iterable[Any]) -> None:
    for item in items or []:
        if item is None:
            continue
        st.write(f"• {item}")


def _compute_risk_score_from_disease_base(
    *,
    possible_concerns_with_percentages: list[str],
    severity_level: str,
) -> tuple[int, str]:
    # Health risk score should depend ONLY on the disease base.
    # We treat the disease base as the set of matched high-risk concerns exposed
    # by the symptom agent via `possible_concerns_with_percentages`.
    #
    # Scoring scheme (educational):
    # - Low severity_level => 25
    # - Medium => 60
    # - High => 85
    # Then, if high-risk concerns are present in the list, we bump within band.

    base_map = {"Low": 25, "Medium": 60, "High": 85}
    score = base_map.get(severity_level, 25)

    # Heuristic bump when high-risk disease-base items are present.
    text = " ".join(possible_concerns_with_percentages or []).lower()
    if "high-risk" in text:
        score = max(score, 85)
    elif "low-risk" in text:
        score = min(score, 60)

    score = max(0, min(int(score), 100))
    severity = "High" if score >= 75 else ("Medium" if score >= 45 else "Low")
    return score, severity



# =========================
# HEADER
# =========================

st.title("🩷 Agentic AI Healthcare Assistant")

st.markdown(
    """
AI-powered healthcare educational assistant using multiple intelligent agents.

### 🔖 Agents Included
- Symptom Analysis Agent
- Diet Recommendation Agent
- Medicine Safety Agent
- Medical Report Generator Agent
"""
)

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=120)
    st.title("Patient Details")

    age: Optional[str] = st.text_input("Age")
    sex: Optional[str] = st.selectbox("Sex", ["Male", "Female", "Other"])
    duration: Optional[str] = st.text_input("Symptoms Duration")
    medical_history: Optional[str] = st.text_area("Medical History", height=120)
    current_meds: Optional[str] = st.text_area("Current Medicines", height=100)

    diet_preference: Optional[str] = st.selectbox(
        "Diet Preference",
        ["None", "Vegetarian", "Vegan", "Low-Sodium", "High-Protein"],
    )

# =========================
# CHAT MEMORY
# =========================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# MAIN INPUT
# =========================

symptoms = st.text_area(
    "Describe Your Symptoms",
    height=180,
    placeholder="Example: Fever, headache, cough, sore throat...",
)

# =========================
# EMERGENCY DETECTION (UI-side warning)
# =========================

emergency_keywords = [
    "chest pain",
    "breathing problem",
    "shortness of breath",
    "unconscious",
    "severe bleeding",
    "heart attack",
    "stroke",
    "fainting",
]

if symptoms and any(word in symptoms.lower() for word in emergency_keywords):
    st.error(
        "🚨 Emergency symptoms detected. Please contact emergency medical services immediately."
    )

# =========================
# BUTTONS
# =========================

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    run_btn = st.button("🩶 Analyze Symptoms", use_container_width=True, type="primary")

with col_btn2:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

with col_btn3:
    workflow_btn = st.button("📄 AI Workflow", use_container_width=True)

    if workflow_btn:
        st.toast("Multi-Agent Workflow Started")
        st.markdown(
            """
## 🩶 AI Agent Pipeline

### 🤙 Symptom Analysis Agent
Detects possible health concerns.

### 🕗 Diet Recommendation Agent
Suggests healthy nutrition plans.

### 💊 Medicine Safety Agent
Gives medicine safety education.

### 📄 Report Generator Agent
Creates final healthcare summary.
"""
        )

# =========================
# CLEAR
# =========================

if clear_btn:
    st.session_state.chat_history = []
    st.rerun()

# =========================
# MAIN AI PROCESSING
# =========================

report = None
score = None
severity = None

if run_btn and symptoms.strip():
    with st.container():
        # -------------------------
        # Symptom Agent
        # -------------------------
        with st.spinner("🩶 Symptom Agent analyzing symptoms..."):
            symptom_result = run_symptom_agent(
                symptoms=symptoms,
                age=age,
                sex=sex,
                duration=duration,
                medical_history=medical_history,
                current_meds=current_meds,
            )

        # -------------------------
        # Diet Agent
        # -------------------------
        with st.spinner("🕗 Diet Agent preparing recommendations..."):
            diet_result = run_diet_agent(
                symptoms=symptoms,
                age=age,
                medical_history=medical_history,
                diet_preference=diet_preference,
            )

        # -------------------------
        # Medicine Agent
        # -------------------------
        with st.spinner("💊 Medicine Agent generating safety guidance..."):
            medicine_result = run_medicine_agent(
                symptoms=symptoms,
                age=age,
                medical_history=medical_history,
                current_meds=current_meds,
            )

        # -------------------------
        # Report Agent
        # -------------------------
        with st.spinner("📄 Report Agent creating medical summary..."):
            report = run_report_agent(
                symptoms=symptoms,
                symptom_severity_level=getattr(symptom_result, "severity_level", "Low"),
                symptom_possible_concerns=_safe_get(symptom_result, "possible_concerns", []),
                symptom_possible_concerns_with_percentages=getattr(
                    symptom_result,
                    "possible_concerns_with_percentages",
                    _safe_get(symptom_result, "possible_concerns", []),
                ),
                symptom_red_flags=_safe_get(symptom_result, "red_flags", []),
                symptom_next_steps=_safe_get(symptom_result, "next_steps", []),
                diet_suggestions=_safe_get(diet_result, "diet_suggestions", []),
                hydration_guidance=_safe_get(diet_result, "hydration_guidance", []),
                medicine_safety_tips=_safe_get(medicine_result, "medication_safety_tips", []),
                clinician_questions=_safe_get(symptom_result, "clinician_questions", []),
                symptom_concern_triggers=_safe_get(symptom_result, "concern_triggers", []),
                symptom_red_flag_triggers=_safe_get(symptom_result, "red_flag_triggers", []),
                age=age,
                sex=sex,
            )

        # -------------------------
        # Save chat history
        # -------------------------
        st.session_state.chat_history.append(
            {"symptoms": symptoms, "report": _safe_get(report, "headline", "")}
        )

        # -------------------------
        # Report header
        # -------------------------
        st.success(_safe_get(report, "headline", "Health summary (educational only)"))

        # -------------------------
        # Risk score + severity (disease-base only)
        # -------------------------
        score, severity = _compute_risk_score_from_disease_base(
            possible_concerns_with_percentages=getattr(
                symptom_result, "possible_concerns_with_percentages", []
            ),
            severity_level=getattr(symptom_result, "severity_level", "Low"),
        )


        st.markdown("## 📌 Health Risk Score")
        st.progress(score)
        st.metric(label="Risk Level", value=f"{score}%")

        # =========================
        # TABS
        # =========================

        tab1, tab2, tab3, tab4 = st.tabs(
            ["🩷 Summary", "🕗 Diet", "💊 Medicine", "🚨 Emergency"]
        )

        # =========================
        # TAB 1: Summary
        # =========================
        with tab1:
            st.markdown("## Possible Concerns (High-risk vs Low-risk)")

            concerns_with_pct = _safe_get(report, "possible_concerns_with_percentages", [])
            concerns_plain = _safe_get(report, "possible_concerns", [])

            items = concerns_with_pct if concerns_with_pct else concerns_plain

            high_items = [x for x in items if isinstance(x, str) and "High-risk" in x]
            low_items = [x for x in items if isinstance(x, str) and "Low-risk" in x]

            other_items = [
                x
                for x in items
                if isinstance(x, str) and x not in set(high_items + low_items)
            ]

            if high_items:
                st.markdown("### 🚨 High-risk possibilities")
                _render_bullets(high_items)

            if low_items:
                st.markdown("### ✅ Low-risk possibilities")
                _render_bullets(low_items)

            if other_items and (high_items or low_items):
                st.markdown("### ℹ️ Other possibilities")
                _render_bullets(other_items)

            st.markdown("## Self Care Steps")
            _render_bullets(_safe_get(report, "self_care_steps", []))

            st.markdown("## Questions For Doctor")
            _render_bullets(_safe_get(report, "questions_to_clinician", []))

        # =========================
        # TAB 2: Diet
        # =========================
        with tab2:
            st.markdown("## Diet Recommendations")
            _render_bullets(_safe_get(report, "diet_recommendations", []))

            st.markdown("## Hydration Guidance")
            _render_bullets(_safe_get(report, "hydration_guidance", []))

        # =========================
        # TAB 3: Medicine
        # =========================
        with tab3:
            st.markdown("## Medication Safety Tips")
            _render_bullets(_safe_get(report, "medicine_safety_tips", []))

        # =========================
        # TAB 4: Emergency
        # =========================
        with tab4:
            st.markdown("## Red Flag Symptoms")
            red_flags = _safe_get(report, "red_flags", [])
            if red_flags:
                for item in red_flags:
                    st.error(item)
            else:
                st.success("No emergency symptoms detected.")

        # =========================
        # ANALYTICS CHART
        # =========================
        st.markdown("## 📈 Health Analytics")
        chart_data = pd.DataFrame(
            {
                "Category": ["Hydration", "Diet", "Medication", "Exercise"],
                "Score": [85, 75, 60, 70],
            }
        )
        st.bar_chart(chart_data.set_index("Category"))

        # =========================
        # DOWNLOAD REPORT
        # =========================
        report_text = f"""
HEALTHCARE AI REPORT

Headline:
{_safe_get(report, 'headline', '')}

Possible Concerns:
{'\n'.join(_safe_get(report, 'possible_concerns', []) or [])}

Red Flags:
{'\n'.join(_safe_get(report, 'red_flags', []) or [])}

Self Care:
{'\n'.join(_safe_get(report, 'self_care_steps', []) or [])}

Diet Recommendations:
{'\n'.join(_safe_get(report, 'diet_recommendations', []) or [])}

Hydration:
{'\n'.join(_safe_get(report, 'hydration_guidance', []) or [])}

Medicine Safety:
{'\n'.join(_safe_get(report, 'medicine_safety_tips', []) or [])}

Disclaimer:
{_safe_get(report, 'disclaimer', '')}
""".strip()

        st.download_button(
            label="📄 Download Full Medical Report",
            data=report_text,
            file_name="healthcare_report.txt",
            mime="text/plain",
        )

# =========================
# CHAT HISTORY
# =========================

if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("# 💬 Previous Conversations")

    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat.get("symptoms", ""))
        with st.chat_message("assistant"):
            st.write(chat.get("report", ""))

# =========================
# FOOTER
# =========================

st.markdown("---")
st.caption("Built using CrewAI + LangChain + Streamlit + Gemini API")

# =========================
# API CHECK
# =========================

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    st.success("✅ Gemini API Key Loaded Successfully")
else:
    st.error("❌ API Key Not Found")

