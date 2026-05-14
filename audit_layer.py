import re


OT_REQUIRED = [
    "assessment",
    "deficits",
    "functional impact",
    "justification",
    "intervention",
]

PHARMACIST_DIMENSION_WEIGHTS = {
    "medication reconciliation": 0.2,
    "dosing specificity": 0.14,
    "schedule/timing clarity": 0.12,
    "adherence clarity": 0.12,
    "safety/counseling quality": 0.14,
    "uncertainty handling": 0.1,
    "escalation appropriateness": 0.08,
    "functional/safety impact linkage": 0.1,
}

UNCERTAINTY_PATTERNS = [
    r"\bmaybe\b",
    r"\bunsure\b",
    r"\bforgot\b",
    r"\bunclear\b",
    r"\bunknown\b",
    r"\bpossibly\b",
    r"\bi think\b",
    r"\bmight be\b",
    r"\bnot sure\b",
]


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _count_matches(text: str, patterns: list[str]) -> int:
    return sum(1 for pattern in patterns if re.search(pattern, text))


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _round_score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _audit_ot_note(lower_text: str) -> dict:
    found = [item for item in OT_REQUIRED if item in lower_text]
    missing = [item for item in OT_REQUIRED if item not in lower_text]
    return {
        "found": found,
        "missing": missing,
        "review_areas": missing,
        "completeness_score": len(found) / len(OT_REQUIRED),
        "review_status": "Additional Review Suggested" if missing else "Draft Ready for Review",
    }


def _audit_pharmacist_note(lower_text: str) -> dict:
    medication_reference_patterns = [
        r"\bmedication(?:s)?\b",
        r"\bsupplement(?:s)?\b",
        r"\bdrug(?:s)?\b",
        r"\bprescription(?:s)?\b",
        r"\bibuprofen\b",
        r"\bmetformin\b",
        r"\bgabapentin\b",
        r"\bturmeric\b",
        r"\binsulin\b",
        r"\bvitamin\b",
    ]
    reconciliation_patterns = [
        r"\bmedication reconciliation\b",
        r"\bcomplete medication\b",
        r"\bcomplete supplement\b",
        r"\bfull medication\b",
        r"\ball current medications\b",
        r"\ball medications and supplements\b",
        r"\bdetailed list\b",
        r"\bmedication list\b",
        r"\bsupplement list\b",
    ]
    dosing_patterns = [
        r"\bdose\b",
        r"\bdosing\b",
        r"\bstrength\b",
        r"\bmg\b",
        r"\bmcg\b",
        r"\bml\b",
        r"\bunits\b",
        r"\btablet\b",
        r"\bcapsule\b",
        r"\broute\b",
    ]
    schedule_patterns = [
        r"\bfrequency\b",
        r"\btiming\b",
        r"\bschedule\b",
        r"\bwhen you take\b",
        r"\bdaily\b",
        r"\btwice daily\b",
        r"\bonce daily\b",
        r"\bevery\b",
    ]
    adherence_patterns = [
        r"\badherence\b",
        r"\bmissed dose(?:s)?\b",
        r"\bskip(?:ped)? dose(?:s)?\b",
        r"\bnot taking regularly\b",
        r"\bbarrier(?:s)?\b",
        r"\bconsistent use\b",
    ]
    safety_patterns = [
        r"\bsafety\b",
        r"\bcounsel(?:ing)?\b",
        r"\binteraction(?:s)?\b",
        r"\bcontraindication(?:s)?\b",
        r"\badverse effect(?:s)?\b",
        r"\bmonitor(?:ing)?\b",
        r"\bdriving\b",
        r"\bfall risk\b",
        r"\bdizziness\b",
        r"\bsedation\b",
    ]
    clarification_patterns = [
        r"\bclarify\b",
        r"\bconfirm\b",
        r"\bverify\b",
        r"\bobtain\b",
        r"\brequest\b",
        r"\brequires clarification\b",
        r"\bnot provided\b",
        r"\bnot available\b",
        r"\bincomplete\b",
    ]
    qualified_language_patterns = [
        r"\bpossible\b",
        r"\bpotential\b",
        r"\bmay\b",
        r"\bcould\b",
        r"\bconcern\b",
        r"\brisk\b",
    ]
    escalation_patterns = [
        r"\bhuman review\b",
        r"\bpharmacist consultation\b",
        r"\bprofessional review\b",
        r"\bfollow-up\b",
        r"\bescalat(?:e|ion)\b",
        r"\bmanual review\b",
        r"\breview is warranted\b",
    ]
    impact_patterns = [
        r"\bsafety concern\b",
        r"\btherapeutic inconsistency\b",
        r"\bsymptom control\b",
        r"\beffectiveness\b",
        r"\bwork\b",
        r"\bdriving\b",
        r"\bfall\b",
        r"\bfatigue\b",
        r"\bconcentration\b",
        r"\bdaily activit(?:y|ies)\b",
    ]

    uncertainty_count = _count_matches(lower_text, UNCERTAINTY_PATTERNS)
    has_medication_reference = _contains_any(lower_text, medication_reference_patterns)
    has_reconciliation_detail = _contains_any(lower_text, reconciliation_patterns)
    has_dose_detail = _contains_any(lower_text, dosing_patterns)
    has_schedule_detail = _contains_any(lower_text, schedule_patterns)
    has_adherence_detail = _contains_any(lower_text, adherence_patterns)
    has_safety_detail = _contains_any(lower_text, safety_patterns)
    has_clarification = _contains_any(lower_text, clarification_patterns)
    has_qualified_language = _contains_any(lower_text, qualified_language_patterns)
    has_escalation = _contains_any(lower_text, escalation_patterns)
    has_impact_linkage = _contains_any(lower_text, impact_patterns)

    uncertain_med_identity = _contains_any(
        lower_text,
        [
            r"\bunknown medication\b",
            r"\bunclear medication\b",
            r"\bnot sure (?:what|which).*(?:medication|supplement)\b",
            r"\bcomplete medication.*not provided\b",
            r"\bmedication list.*not provided\b",
        ],
    )
    uncertain_dosing = _contains_any(
        lower_text,
        [
            r"\bdose.*not (?:provided|available|clear)\b",
            r"\bfrequency.*not (?:provided|available|clear)\b",
            r"\btiming.*not (?:provided|available|clear)\b",
            r"\buncertain about (?:dose|timing|schedule)\b",
            r"\bexact timing.*unclear\b",
        ],
    )
    overclaimed_interaction = _contains_any(
        lower_text,
        [r"\bdefinitive interaction\b", r"\bwill interact\b", r"\bconfirmed interaction\b"],
    ) and not has_qualified_language

    explicit_dose_detail = _contains_any(
        lower_text,
        [r"\bmg\b", r"\bmcg\b", r"\bml\b", r"\bunits\b", r"\bstrength\b", r"\broute\b", r"\bamount\b"],
    )
    verified_schedule = _contains_any(lower_text, [r"\bverified\b", r"\bclear timing\b", r"\bclear schedule\b", r"\bconsistent timing\b"])
    adherence_support = _contains_any(
        lower_text,
        [r"\bbarrier(?:s)?\b", r"\badherence support\b", r"\breviewed\b", r"\bconsistent use\b", r"\bcounsel(?:ing)?\b"],
    )
    complete_reconciliation = _contains_any(
        lower_text,
        [r"\breconciliation completed\b", r"\ball current medications\b", r"\ball medications and supplements\b", r"\bcomplete medication\b", r"\bfull medication\b"],
    )
    functional_linkage_support = _contains_any(
        lower_text,
        [r"\bdiscussed\b", r"\baddressed\b", r"\bexplained\b", r"\bdocumented\b", r"\bmay impact\b", r"\bcould reduce\b", r"\bincrease risk\b", r"\bcontribute to\b"],
    )

    dimension_scores = {
        "medication reconciliation": min(
            1.0,
            (0.25 if has_medication_reference else 0.0)
            + (0.45 if complete_reconciliation or has_reconciliation_detail else 0.0)
            + (0.15 if _contains_any(lower_text, [r"\bindication\b", r"\bsupplement list\b", r"\bmedication list\b"]) else 0.0)
            + (0.15 if has_clarification else 0.0),
        ),
        "dosing specificity": min(
            1.0,
            (0.35 if has_dose_detail else 0.0)
            + (0.3 if explicit_dose_detail else 0.0)
            + (0.15 if _contains_any(lower_text, [r"\bverified\b", r"\bconfirmed\b"]) else 0.0)
            + (0.2 if has_clarification and not uncertain_dosing else 0.0),
        ),
        "schedule/timing clarity": min(
            1.0,
            (0.55 if has_schedule_detail else 0.0)
            + (0.25 if verified_schedule else 0.0)
            + (0.2 if has_clarification and not uncertain_dosing else 0.0),
        ),
        "adherence clarity": min(
            1.0,
            (0.45 if has_adherence_detail else 0.0)
            + (0.25 if adherence_support else 0.0)
            + (0.15 if has_escalation else 0.0)
            + (0.15 if _contains_any(lower_text, [r"\bfollow-up\b", r"\bmonitor\b"]) else 0.0),
        ),
        "safety/counseling quality": min(
            1.0,
            (0.45 if has_safety_detail else 0.0)
            + (0.25 if _contains_any(lower_text, [r"\bmonitor\b", r"\beducat(?:e|ion)\b", r"\bcounsel\b"]) else 0.0)
            + (0.15 if has_escalation else 0.0)
            + (0.15 if has_qualified_language else 0.0),
        ),
        "escalation appropriateness": min(
            1.0,
            (0.7 if has_escalation else 0.0)
            + (0.3 if _contains_any(lower_text, [r"\bfollow-up\b", r"\breview is warranted\b"]) else 0.0),
        ),
        "functional/safety impact linkage": min(
            1.0,
            (0.45 if has_impact_linkage else 0.0)
            + (0.25 if _contains_any(lower_text, [r"\bimpact\b", r"\bsymptom control\b", r"\btherapeutic inconsistency\b"]) else 0.0)
            + (0.3 if functional_linkage_support else 0.0),
        ),
    }

    if uncertain_med_identity:
        dimension_scores["medication reconciliation"] = min(dimension_scores["medication reconciliation"], 0.55)
    if uncertain_dosing:
        dimension_scores["dosing specificity"] = min(dimension_scores["dosing specificity"], 0.35)
        dimension_scores["schedule/timing clarity"] = min(dimension_scores["schedule/timing clarity"], 0.4)

    if uncertainty_count:
        uncertainty_score = 0.2
        if has_clarification:
            uncertainty_score += 0.4
        if has_qualified_language:
            uncertainty_score += 0.25
        if has_escalation:
            uncertainty_score += 0.15
    elif overclaimed_interaction:
        uncertainty_score = 0.35
    else:
        uncertainty_score = 1.0 if not overclaimed_interaction else 0.35

    dimension_scores["uncertainty handling"] = min(1.0, uncertainty_score)

    safety_combo_checks = [
        ([r"\bdizziness\b", r"\bnear fall\b|\bfall risk\b|\bfall\b"], "fall-risk counseling incomplete"),
        ([r"\bsedation\b|\bdrows(?:y|iness)\b", r"\bdriving\b"], "driving safety counseling incomplete"),
        ([r"\bskip(?:ped)? dose(?:s)?\b|\bmissed dose(?:s)?\b", r"\bwork\b|\bjob\b"], "work-safety concerns unresolved"),
        ([r"\bcns\b|\bgabapentin\b|\bsedation\b", r"\bfatigue\b"], "fatigue-related medication safety review needed"),
        ([r"\bunclear\b|\bunknown\b|\bnot sure\b", r"\bdizziness\b|\bsymptom\b|\bcomplaint\b"], "symptom review requires dose clarification"),
        ([r"\bworkers comp\b|\bwork-related\b", r"\bconcentration\b|\bfatigue\b"], "workers compensation safety review needed"),
        ([r"\belderly\b|\bolder adult\b", r"\bfall\b|\bnear fall\b|\bfall risk\b"], "elder fall-risk counseling incomplete"),
        ([r"\bdouble dosing\b|\bdouble dose\b", r"\bmedication\b|\bdose\b"], "double-dosing behavior requires escalation"),
        ([r"\badherence\b|\bskip(?:ped)? dose(?:s)?\b|\bmissed dose(?:s)?\b", r"\binconsistent\b|\bunclear\b"], "adherence inconsistency remains unresolved"),
    ]

    safety_flags = [
        label for patterns, label in safety_combo_checks if all(re.search(pattern, lower_text) for pattern in patterns)
    ]

    review_areas: list[str] = []
    if dimension_scores["medication reconciliation"] < 0.7:
        review_areas.append("medication reconciliation incomplete")
    if dimension_scores["dosing specificity"] < 0.65 or uncertain_dosing:
        review_areas.append("exact dosing unresolved")
    if dimension_scores["schedule/timing clarity"] < 0.65:
        review_areas.append("medication timing unclear")
    if dimension_scores["adherence clarity"] < 0.65:
        review_areas.append("adherence clarification needed")
    if dimension_scores["safety/counseling quality"] < 0.7:
        review_areas.append("safety or counseling review needed")
    if dimension_scores["uncertainty handling"] < 0.75 and uncertainty_count:
        review_areas.append("uncertainty needs clarification")
    if dimension_scores["escalation appropriateness"] < 0.7:
        review_areas.append("review escalation should be documented")
    if dimension_scores["functional/safety impact linkage"] < 0.65:
        review_areas.append("functional or safety impact linkage incomplete")
    if overclaimed_interaction:
        review_areas.append("interaction certainty should be qualified")
    review_areas.extend(safety_flags)
    review_areas = _dedupe(review_areas)

    weighted_score = sum(
        PHARMACIST_DIMENSION_WEIGHTS[name] * dimension_scores[name]
        for name in PHARMACIST_DIMENSION_WEIGHTS
    )
    penalty = min(0.18, uncertainty_count * 0.035) + min(0.2, len(safety_flags) * 0.05)
    if uncertain_med_identity:
        penalty += 0.08
    if overclaimed_interaction:
        penalty += 0.1
    completeness_score = max(0.0, weighted_score - penalty)

    score_caps: list[float] = []
    if uncertain_med_identity:
        score_caps.append(0.75)
    if uncertain_dosing or dimension_scores["dosing specificity"] < 0.55:
        score_caps.append(0.8)
    if dimension_scores["schedule/timing clarity"] < 0.55:
        score_caps.append(0.8)
    if len(review_areas) >= 4:
        score_caps.append(0.7)
    if len(safety_flags) >= 2:
        score_caps.append(0.7)
    if score_caps:
        completeness_score = min(completeness_score, min(score_caps))

    found = [name for name, score in dimension_scores.items() if score >= 0.7]
    review_status = (
        "Mandatory Human Review"
        if safety_flags
        or uncertain_med_identity
        or completeness_score < 0.78
        or len(review_areas) >= 4
        else "Standard Human Review"
    )

    return {
        "found": found,
        "missing": review_areas,
        "review_areas": review_areas,
        "completeness_score": _round_score(completeness_score),
        "review_status": review_status,
        "dimension_scores": {name: _round_score(score) for name, score in dimension_scores.items()},
        "uncertainty_count": uncertainty_count,
        "safety_flags": safety_flags,
    }


def audit_clinical_note(text: str, practitioner_type: str):
    pt = practitioner_type.lower()

    if pt == "occupational therapist":
        return _audit_ot_note(text.lower())
    if pt == "pharmacist":
        return _audit_pharmacist_note(text.lower())

    return {"error": "Unsupported practitioner type"}