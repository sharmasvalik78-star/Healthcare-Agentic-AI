from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MedicineEducation:
    general_information: List[str]
    medication_safety_tips: List[str]
    questions_to_clinician: List[str]


def run_medicine_agent(
    *,
    symptoms: str,
    age: Optional[str] = None,
    medical_history: Optional[str] = None,
    current_meds: Optional[str] = None,
) -> MedicineEducation:
    # Heuristic fallback (safe, non-prescriptive)
    s = (symptoms or "").lower()

    general: List[str] = [
        "Common symptom relief options depend on the cause; a clinician can recommend options that fit your history.",
        "Avoid starting new medications without confirming compatibility with your current medications/conditions.",
    ]

    safety: List[str] = [
        "Check labels for active ingredients to avoid double-dosing (especially cold/flu products).",
        "If you have kidney/liver disease, pregnancy, or stomach bleeding history, ask a clinician before using OTC pain relievers.",
        "Do not exceed recommended doses; stop and seek care if you develop allergic symptoms or severe side effects.",
    ]

    if any(k in s for k in ["cough", "congestion"]):
        safety.insert(0, "For cough/congestion products, check whether they contain decongestants or sedating ingredients that may not be appropriate for everyone.")

    questions: List[str] = [
        "Which symptom-relief options are appropriate for me given my medical history?",
        "Are any of my current medications likely to interact with OTC options?",
        "What warning signs mean I should stop self-care and get urgent help?",
        "If symptoms persist, what next step (tests or referral) should be considered?",
    ]

    return MedicineEducation(
        general_information=general[:5],
        medication_safety_tips=safety[:5],
        questions_to_clinician=questions[:5],
    )

