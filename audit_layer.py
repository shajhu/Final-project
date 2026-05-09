def audit_clinical_note(text: str, practitioner_type: str):
    REQUIRED = {
        "occupational therapist": [
            "assessment",
            "deficits",
            "functional impact",
            "justification",
            "intervention",
        ],
        "pharmacist": [
            "medication",
            "adherence",
            "interaction",
            "recommendation",
        ],
    }

    pt = practitioner_type.lower()

    if pt not in REQUIRED:
        return {"error": "Unsupported practitioner type"}

    lower_text = text.lower()

    found = []
    missing = []

    for item in REQUIRED[pt]:
        if item in lower_text:
            found.append(item)
        else:
            missing.append(item)

    return {
        "found": found,
        "missing": missing,
        "completeness_score": len(found) / len(REQUIRED[pt]),
    }