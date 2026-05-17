from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DietPlan:
    diet_suggestions: List[str]
    hydration_guidance: List[str]
    avoid_list: List[str]
    clinician_questions: List[str]


def _infer_basic_diet_preferences(symptoms: str, diet_preference: Optional[str]) -> List[str]:
    s = (symptoms or "").lower()
    prefs: List[str] = []

    if "sore throat" in s or "throat" in s or "cough" in s:
        prefs.append("Warm fluids (tea/soups) and soothing options like honey (if appropriate for you).")
    if any(k in s for k in ["nausea", "vomit", "stomach"]):
        prefs.append("Small, bland meals; consider BRAT-style foods if they help you feel better.")
    if any(k in s for k in ["diarrhea", "loose stool"]):
        prefs.append("Focus on bland, low-fat foods and replace fluids/electrolytes.")

    if not prefs:
        prefs.append("A balanced diet with adequate protein and calories, adjusted to symptom triggers.")

    if diet_preference:
        p = diet_preference.strip().lower()
        prefs.insert(0, f"Align suggestions with your preference: {diet_preference}.")
        # Keep generic; actual constraint handling can be improved later.

    return prefs


def run_diet_agent(
    *,
    symptoms: str,
    age: Optional[str] = None,
    medical_history: Optional[str] = None,
    diet_preference: Optional[str] = None,
) -> DietPlan:
    # Heuristic fallback (LLM wiring can replace later)
    diet = _infer_basic_diet_preferences(symptoms, diet_preference)

    hydration: List[str] = [
        "Aim for steady fluid intake; include water and calorie-free drinks if appropriate.",
        "If you have vomiting/diarrhea, consider oral rehydration solution or electrolyte drinks.",
    ]

    avoid: List[str] = [
        "Avoid foods that clearly worsen your symptoms (spicy, very acidic, or high-fat items if they trigger you).",
        "Avoid alcohol and excessive caffeine when you feel unwell.",
    ]

    questions: List[str] = [
        "Do my medical conditions (if any) require dietary restrictions?",
        "Are there specific foods or supplements I should avoid with my medications?",
        "Should I follow a temporary diet while symptoms settle?",
    ]

    return DietPlan(
        diet_suggestions=diet[:5],
        hydration_guidance=hydration[:4],
        avoid_list=avoid[:4],
        clinician_questions=questions[:4],
    )

