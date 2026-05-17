from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


def _build_symptom_prompt(user_input: str) -> str:
    return f"""
You are a careful healthcare triage assistant (educational only).

Task: Analyze the user's symptoms and produce:
1) Possible concerns (non-diagnostic, general language)
2) Red flags (urgent/emergency signals)
3) Self-care / next steps suggestions
4) Questions to ask a clinician

Rules:
- Do NOT diagnose.
- Do NOT claim certainty.
- Emphasize that this is not medical advice.
- If red flags are present, strongly advise seeking urgent care or emergency services.
- Keep output structured and concise.

User input:
{user_input}
""".strip()


@dataclass
class SymptomAnalysis:
    possible_concerns: List[str]
    # Educational/heuristic estimated likelihoods that sum to ~100.
    # Not medical probabilities.
    possible_concerns_with_percentages: List[str]

    red_flags: List[str]
    # High/Medium/Low severity derived from detected red flags (educational only)
    severity_level: str
    next_steps: List[str]
    clinician_questions: List[str]

    # Educational rationale (used by UI to show what triggered matches)
    concern_triggers: List[List[str]]
    red_flag_triggers: List[List[str]]




def run_symptom_agent(
    *,
    symptoms: str,
    age: Optional[str] = None,
    sex: Optional[str] = None,
    duration: Optional[str] = None,
    medical_history: Optional[str] = None,
    current_meds: Optional[str] = None,
) -> SymptomAnalysis:
    """Heuristic fallback when no LLM is configured."""

    # Basic keyword triage (negation-aware).
    s = (symptoms or "").lower()

    def _is_negated(phrase: str) -> bool:
        # Lightweight negation heuristic:
        # if a negation word appears in a short window before the phrase, treat as negated.
        negators = ["no ", "not ", "denies ", "denied ", "without ", "can't ", "cannot ", "won't "]
        idx = s.find(phrase)
        if idx < 0:
            return False
        window_start = max(0, idx - 40)
        window = s[window_start:idx]
        return any(n in window for n in negators)

    red_flags: List[str] = []
    red_flag_triggers: List[List[str]] = []

    chest_triggers = ["chest pain", "pressure", "can't breathe", "shortness of breath", "sob", "faint", "fainted"]
    matched_chest = [t for t in chest_triggers if t in s and not _is_negated(t)]
    if matched_chest:
        red_flags.append("Chest pain/pressure or trouble breathing can be an emergency—seek urgent/emergency care.")
        red_flag_triggers.append(matched_chest)

    headache_triggers = ["severe headache", "worst headache", "sudden"]
    matched_headache = [t for t in headache_triggers if t in s and not _is_negated(t)]
    if matched_headache:
        red_flags.append("Severe or sudden headache can be urgent—consider urgent care/emergency evaluation.")
        red_flag_triggers.append(matched_headache)

    bleeding_triggers = ["blood", "vomiting blood", "black stool", "tarry"]
    matched_bleeding = [t for t in bleeding_triggers if t in s and not _is_negated(t)]
    if matched_bleeding:
        red_flags.append("Possible bleeding symptoms—seek urgent care.")
        red_flag_triggers.append(matched_bleeding)

    stroke_triggers = ["weakness on one side", "slurred speech", "face droop", "stroke"]
    matched_stroke = [t for t in stroke_triggers if t in s and not _is_negated(t)]
    if matched_stroke:
        red_flags.append("Stroke-like symptoms—seek emergency services immediately.")
        red_flag_triggers.append(matched_stroke)

    fever_triggers = ["high fever", "103", "104", "very high"]
    matched_fever = [t for t in fever_triggers if t in s and not _is_negated(t)]
    if matched_fever:
        red_flags.append("Very high fever—consider prompt medical evaluation.")
        red_flag_triggers.append(matched_fever)

    # Generic concerns
    possible: List[str] = []
    possible_scores: List[int] = []
    concern_triggers: List[List[str]] = []

    concern_risk_by_name: List[str] = []  # "high" | "low"

    def _add_concern(name: str, matched: List[str], base: int = 30, risk: str = "low") -> None:
        # Deterministic educational scoring:
        # - start with base points
        # - add per matched signal (up to a small cap)
        per_signal = 10
        cap = 3
        extra = min(len(matched), cap) * per_signal
        score = base + extra
        possible.append(name)
        possible_scores.append(score)
        concern_triggers.append(matched)
        concern_risk_by_name.append(risk)


    # -------------------------
    # Low-risk “more common / less specific” patterns
    # -------------------------
    uri_triggers = ["cough", "sore throat", "fever", "congestion"]
    matched_uri = [t for t in uri_triggers if t in s and not _is_negated(t)]
    if matched_uri:
        _add_concern(
            "Low-risk: Viral upper respiratory infection (one of several possibilities)",
            matched_uri,
            base=30,
            risk="low",
        )

    uti_triggers = ["burning when urinating", "urine", "frequency"]
    matched_uti = [t for t in uti_triggers if t in s and not _is_negated(t)]
    if matched_uti:
        _add_concern(
            "Low-risk: Urinary tract irritation/infection (not a diagnosis)",
            matched_uti,
            base=25,
            risk="low",
        )

    gi_triggers = ["nausea", "vomit", "stomach"]
    matched_gi = [t for t in gi_triggers if t in s and not _is_negated(t)]
    if matched_gi:
        _add_concern(
            "Low-risk: Gastrointestinal upset (many causes)",
            matched_gi,
            base=25,
            risk="low",
        )

    pain_triggers = ["pain", "cramp"]
    matched_pain = [t for t in pain_triggers if t in s and not _is_negated(t)]
    if matched_pain:
        _add_concern(
            "Low-risk: Pain/inflammation-related causes (broad possibilities)",
            matched_pain,
            base=25,
            risk="low",
        )

    # -------------------------
    # High-risk “urgent / potentially serious” patterns
    # (These overlap with red flags above; we also surface them here as “high risk diseases”.)
    # -------------------------
    high_risk_disease_triggers = [
        "chest pain",
        "shortness of breath",
        "breathing problem",
        "stroke",
        "heart attack",
        "severe fever",
        "high fever",
        "diabetes",
        "epilepsy",
        "hypertension",
        "asthma",
        "cancer",
        "kidney failure",
    ]

    matched_high_risk = [t for t in high_risk_disease_triggers if t in s and not _is_negated(t)]
    if matched_high_risk:
        _add_concern(
            "High-risk: Potentially serious condition(s) possible—seek urgent clinician guidance if symptoms fit.",
            matched_high_risk,
            base=35,
            risk="high",
        )


    if not possible:
        possible.append("A range of possibilities depending on context (needs clarification)")
        possible_scores.append(1)
        concern_triggers.append([])

    # Convert scores to integer percentages that sum to 100 (approx).
    total = sum(possible_scores) or 1
    raw = [s / total * 100 for s in possible_scores]
    floored = [int(x) for x in raw]
    remainder = 100 - sum(floored)
    # Distribute remainder to largest fractional parts
    fractional = [(i, raw[i] - floored[i]) for i in range(len(raw))]
    fractional.sort(key=lambda t: t[1], reverse=True)
    for k in range(remainder):
        idx = fractional[k % len(fractional)][0]
        floored[idx] += 1

    possible_with_percentages = [f"{name} — {pct}%" for name, pct in zip(possible, floored)]

    next_steps: List[str] = [

        "Consider monitoring symptoms and vital signs (temperature, hydration, pain level).",
        "If symptoms are worsening or persistent, consider seeing a clinician.",
        "Stay hydrated and rest; use over-the-counter options only if appropriate for you.",
    ]
    if duration and any(w in duration.lower() for w in ["weeks", "month"]):
        next_steps.insert(1, "Because symptoms have lasted a while, booking a medical evaluation is advisable.")

    clinician_questions: List[str] = [
        "Could these symptoms be caused by something serious?",
        "What tests (if any) are recommended and why?",
        "What red flags should I watch for at home?",
        "What treatment options are safe with my medical history/medications?",
    ]

    # Derive an overall severity level from how many red flags matched.
    # - High: 2+ red flags matched
    # - Medium: 1 red flag matched
    # - Low: none detected
    num_red_flags = len(red_flags)
    if num_red_flags >= 2:
        severity_level = "High"
    elif num_red_flags == 1:
        severity_level = "Medium"
    else:
        severity_level = "Low"

    # Keep lists aligned with the UI caps.
    return SymptomAnalysis(
        possible_concerns=possible[:5],
        possible_concerns_with_percentages=possible_with_percentages[:5],
        red_flags=red_flags[:5],
        severity_level=severity_level,

        next_steps=next_steps[:5],
        clinician_questions=clinician_questions[:5],
        concern_triggers=concern_triggers[:5],
        red_flag_triggers=red_flag_triggers[:5],
    )



