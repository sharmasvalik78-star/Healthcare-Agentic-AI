from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HealthReport:
    headline: str
    possible_concerns: List[str]
    # Educational/heuristic estimated likelihoods that sum to ~100.
    possible_concerns_with_percentages: List[str]
    red_flags: List[str]


    # Derived from symptom red flag matches (educational only)
    severity_level: str

    # Educational rationale (optional)
    concern_triggers: List[List[str]]
    red_flag_triggers: List[List[str]]


    self_care_steps: List[str]
    diet_recommendations: List[str]
    hydration_guidance: List[str]
    medicine_safety_tips: List[str]
    questions_to_clinician: List[str]
    disclaimer: str


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def run_report_agent(
    *,
    symptoms: str,
    symptom_severity_level: str = "Low",

    symptom_possible_concerns: List[str],
    symptom_possible_concerns_with_percentages: List[str],
    symptom_red_flags: List[str],
    symptom_next_steps: List[str],

    diet_suggestions: List[str],
    hydration_guidance: List[str],
    medicine_safety_tips: List[str],
    clinician_questions: List[str],
    symptom_concern_triggers: List[List[str]],
    symptom_red_flag_triggers: List[List[str]],
    age: Optional[str] = None,
    sex: Optional[str] = None,
) -> HealthReport:
    # Deterministic consolidation (LLM can be added later)
    age_sex = ", ".join([x for x in [age, sex] if x])
    headline = "Health summary (educational only)"
    if age_sex:
        headline = f"Health summary for {age_sex} (educational only)"

    possible_concerns_with_percentages = symptom_possible_concerns_with_percentages

    return HealthReport(
        headline=headline,

        possible_concerns=_dedupe_keep_order(symptom_possible_concerns)[:6],
        possible_concerns_with_percentages=_dedupe_keep_order(possible_concerns_with_percentages)[:6],
        red_flags=_dedupe_keep_order(symptom_red_flags)[:6],

        severity_level=symptom_severity_level,

        concern_triggers=symptom_concern_triggers[:5],
        red_flag_triggers=symptom_red_flag_triggers[:5],
        self_care_steps=_dedupe_keep_order(symptom_next_steps)[:6],
        diet_recommendations=_dedupe_keep_order(diet_suggestions)[:6],
        hydration_guidance=_dedupe_keep_order(hydration_guidance)[:5],
        medicine_safety_tips=_dedupe_keep_order(medicine_safety_tips)[:6],
        questions_to_clinician=_dedupe_keep_order(clinician_questions)[:8],
        disclaimer=(
            "This application provides educational information and symptom support only. "
            "It is not medical advice and cannot diagnose or replace professional care. "
            "If you feel seriously unwell or have emergency warning signs, seek urgent/emergency medical help."
        ),
    )

