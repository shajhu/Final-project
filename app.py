# API key is loaded from .env for local development
# Do not hardcode secrets

import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from audit_layer import audit_clinical_note
from model_adapter import ClaudeAdapter, OpenAIAdapter

load_dotenv()

MODEL_NAME = "gpt-4.1-mini"  # If model access fails, gpt-4o-mini may be used as a fallback.
MODEL_PROVIDER = "openai"
BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
USAGE_FILE = BASE_DIR / "usage.json"
USE_ASSIGNMENT_FORMAT = True
APP_LOGO_PATH = BASE_DIR / "assets" / "draftsafe_logo_bw.png"
APP_LOGO_BASE64 = base64.b64encode(APP_LOGO_PATH.read_bytes()).decode("ascii") if APP_LOGO_PATH.exists() else ""
APP_NAME = "DraftSafe™"
APP_TAGLINE = "AI-Assisted Practitioner Documentation & Review"
APP_SUBTITLE = "AI-assisted drafting, deterministic auditing, and human review support."
COPYRIGHT_NOTICE = "© 2026 Shamir Dominique. All rights reserved."
DRAFTSAFE_OWNERSHIP_NOTICE = (
    "DraftSafe™ and its associated workflow concepts, interface structure, deterministic audit integration logic, "
    "practitioner-assistive workflows, and supporting materials were independently developed by Shamir Dominique.\n\n"
    "No portion of this repository, workflow, interface, exported outputs, or supporting implementation may be reproduced, redistributed, reverse engineered, or commercialized without explicit written permission from the author."
)
APP_FOOTER_LINES = [
    "DraftSafe™ - AI-Assisted Practitioner Documentation & Review",
    COPYRIGHT_NOTICE,
    "Prototype system independently developed by Shamir Dominique for educational, workflow-support, research, and demonstration purposes.",
    "This system does not replace licensed clinical judgment, medical advice, or professional review.",
    "Unauthorized reproduction, redistribution, reverse engineering, or commercialization of this workflow, interface, audit structure, or supporting implementation without written permission is prohibited.",
]
SECTION_HEADER_ALLOWLIST = {
    "Findings",
    "Assessment",
    "Deficits",
    "Functional Impact",
    "Justification",
    "Intervention",
    "Suggested Next Actions",
    "Individual-Facing Summary",
    "QC Review",
    "Review Status",
    "Clinical Note",
    "Key Highlights",
    "Next Steps",
    "Flagged Concerns",
    "Human Review",
    "Standard Human Review",
    "Mandatory Human Review",
    "Attached Intake/Form Content",
}

PRACTITIONER_KNOWLEDGE_MAP = {
    "Occupational Therapist": {
        "focus": "functional performance, ADLs/IADLs, mobility, safety, motor control, therapy justification",
        "trigger_terms": [
            "proprioceptive input",
            "fatigue",
            "muscular weakness",
            "mobility deficits",
            "workers comp",
            "home exercise program",
            "load tolerance",
            "body mechanics",
            "fall prevention",
            "injury avoidance",
            "motor control",
            "balance",
            "coordination",
            "adl",
            "iadl",
            "functional independence",
        ],
        "documentation_needs": [
            "key findings",
            "deficits",
            "functional impact",
            "justification for skilled therapy",
            "intervention direction",
            "safety concerns",
        ],
        "source_note": "Use OT terminology consistent with AOTA OTPF concepts such as occupations, performance skills, client factors, ADLs/IADLs, and functional participation. Use CDC STEADI concepts when fall risk or fall prevention is present.",
    },
    "Nurse": {
        "focus": "patient safety, medication administration, monitoring, care coordination, symptom escalation",
        "trigger_terms": [
            "medication",
            "dose",
            "units",
            "mL",
            "cc",
            "route",
            "frequency",
            "administer",
            "storage",
            "inventory",
            "missed dose",
            "side effect",
            "allergy",
            "vital signs",
            "blood pressure",
            "blood glucose",
            "insulin",
            "injection",
            "wound",
            "fever",
        ],
        "documentation_needs": [
            "accurate medication amount",
            "route",
            "timing",
            "dose units",
            "monitoring needs",
            "safety concerns",
            "escalation criteria",
            "care coordination needs",
        ],
        "source_note": "Use medication safety concepts aligned with the rights of medication administration and medication-error prevention. Do not calculate or convert doses unless explicitly provided and verified by the user.",
    },
    "Pharmacist": {
        "focus": "medication review, supplement review, contraindication screening, adherence, counseling points",
        "trigger_terms": [
            "medication",
            "supplement",
            "vitamin",
            "interaction",
            "contraindication",
            "allergy",
            "side effect",
            "adherence",
            "dose",
            "frequency",
            "blood thinner",
            "pregnant",
            "liver",
            "kidney",
            "renal",
            "hepatic",
        ],
        "documentation_needs": [
            "medication/supplement list clarity",
            "interaction concern flag",
            "adherence concern",
            "counseling point",
            "professional review requirement",
            "escalation criteria",
        ],
        "source_note": "Use medication safety and pharmacy review language. Do not claim a definitive interaction unless explicitly supported by the supplied intake or a curated source.",
    },
    "Wellness Consultant": {
        "focus": "goals, preferences, lifestyle context, education, non-diagnostic wellness guidance",
        "trigger_terms": [
            "sleep",
            "stress",
            "energy",
            "focus",
            "relaxation",
            "routine",
            "preference",
            "caffeine",
            "exercise",
            "nutrition",
            "hydration",
        ],
        "documentation_needs": [
            "goals",
            "preferences",
            "current habits",
            "education needs",
            "general next steps",
            "review boundaries",
            "referral/escalation if risk flags appear",
        ],
        "source_note": "Use general wellness education language only. Avoid diagnosis, treatment claims, or medical directives.",
    },
    "General Medical Reviewer": {
        "focus": "intake organization, safety triage, missing information, escalation needs",
        "trigger_terms": [
            "pain",
            "dizziness",
            "chest pain",
            "shortness of breath",
            "confusion",
            "severe",
            "emergency",
            "medication",
            "allergy",
            "fall",
            "pregnant",
        ],
        "documentation_needs": [
            "key findings",
            "missing information",
            "risk flags",
            "review status",
            "escalation recommendation",
        ],
        "source_note": "Use conservative intake-review language and escalate unclear or high-risk issues.",
    },
}

PRACTITIONER_TRIGGER_GROUPS = {
    "Occupational Therapist": [
        ("fatigue", ["fatigue", "tired", "low energy", "exhaust", "endurance"]),
        ("motor control / coordination", ["coordination", "motor control", "hand coordination", "dexterity", "fine motor", "grip"]),
        ("muscular weakness", ["weakness", "grip strength", "decreased grip", "hand weakness", "reduced strength"]),
        ("mobility / balance issues", ["imbalance", "balance", "unsteady", "mobility", "walking difficulty", "gait"]),
        ("fall risk", ["fall", "fall risk", "near fall", "stumble"]),
        ("body mechanics", ["body mechanics", "lifting", "posture", "ergonomic", "mechanics"]),
        ("workers comp relevance", ["workers comp", "work injury", "job", "physically demanding job", "work-related"]),
        ("load tolerance", ["load tolerance", "activity tolerance", "prolonged activity", "sustained activity"]),
        ("home exercise program", ["home exercise", "home program", "exercise program"]),
        ("ADLs/IADLs", ["adl", "adls", "iadl", "iadls", "daily activities", "independently"]),
    ],
    "Pharmacist": [
        ("medication use", ["medication", "medicine", "ibuprofen", "prescription", "drug"]),
        ("supplement use", ["supplement", "turmeric", "vitamin", "herbal", "herb"]),
        ("adherence issues", ["skip doses", "missed doses", "sometimes skips", "adherence", "not taking regularly", "unclear on dosing"]),
        ("side effects", ["side effect", "stomach discomfort", "dizziness", "nausea", "upset stomach"]),
        ("potential interaction concern", ["interaction", "combination", "taking with", "co-use", "with turmeric"]),
        ("allergy", ["allergy", "allergies"]),
        ("dose / schedule clarity", ["dose", "dosing", "schedule", "frequency", "timing"]),
    ],
    "Nurse": [
        ("medication", ["medication", "medicine", "drug"]),
        ("dose / units", ["dose", "units", "ml", "cc"]),
        ("route / administration", ["route", "administer", "injection", "oral", "iv"]),
        ("monitoring needs", ["monitor", "vital signs", "blood pressure", "blood glucose", "fever"]),
        ("safety concerns", ["allergy", "missed dose", "side effect", "wound"]),
    ],
    "Wellness Consultant": [
        ("sleep", ["sleep", "rest"]),
        ("stress", ["stress", "overwhelm", "burnout"]),
        ("energy", ["energy", "fatigue", "tired"]),
        ("routine / lifestyle", ["routine", "schedule", "habit", "lifestyle"]),
        ("nutrition / hydration", ["nutrition", "diet", "hydration", "water"]),
    ],
    "General Medical Reviewer": [
        ("pain", ["pain", "ache"]),
        ("dizziness", ["dizziness", "lightheaded", "vertigo"]),
        ("fall risk", ["fall", "near fall", "imbalance"]),
        ("medication concern", ["medication", "dose", "allergy"]),
        ("escalation concern", ["chest pain", "shortness of breath", "confusion", "emergency", "severe"]),
    ],
}

st.set_page_config(page_title=APP_NAME, layout="centered")

# Session state used to persist PID toggle across Streamlit reruns
if "ALLOW_PID" not in st.session_state:
    st.session_state["ALLOW_PID"] = False
if "run_incremented" not in st.session_state:
    st.session_state["run_incremented"] = False
if "draft_data" not in st.session_state:
    st.session_state["draft_data"] = None
if "last_intake_text" not in st.session_state:
    st.session_state["last_intake_text"] = ""
if "generated_output" not in st.session_state:
    st.session_state["generated_output"] = ""
if "save_success_message" not in st.session_state:
    st.session_state["save_success_message"] = ""
if "save_success_path" not in st.session_state:
    st.session_state["save_success_path"] = ""
if "save_incomplete_warning" not in st.session_state:
    st.session_state["save_incomplete_warning"] = ""


def default_usage_data() -> dict:
    return {
        "total_runs": 0,
        "total_reviews_submitted": 0,
        "audit_score_sum": 0.0,
        "audit_score_count": 0,
        "missing_section_counts": {},
        "total_reviews": 0,
        "total_score": 0.0,
        "average_score": 0,
        "audit_runs": 0,
    }


def safe_dashboard_value(value: Any, fallback: Any = "None") -> Any:
    """
    Prevent dashboard crashes from empty or invalid analytics values.
    """
    if value is None:
        print("[Dashboard] Safe fallback applied for empty analytics state")
        return fallback

    if isinstance(value, dict) and not value:
        print("[Dashboard] Safe fallback applied for empty analytics state")
        return fallback

    if isinstance(value, list) and not value:
        print("[Dashboard] Safe fallback applied for empty analytics state")
        return fallback

    if isinstance(value, str) and value.strip() == "":
        print("[Dashboard] Safe fallback applied for empty analytics state")
        return fallback

    return value


def safe_average(total_score, total_reviews):
    return total_score / total_reviews if total_reviews > 0 else 0


def initialize_usage() -> None:
    if not USAGE_FILE.exists():
        USAGE_FILE.write_text(
            json.dumps(default_usage_data(), indent=2),
            encoding="utf-8",
        )
        return

    try:
        data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = default_usage_data()

    changed = False
    for key, value in default_usage_data().items():
        if key not in data:
            data[key] = value
            changed = True

    if changed:
        USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_usage() -> dict:
    try:
        data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return default_usage_data()

    defaults = default_usage_data()
    defaults.update(data)
    if not isinstance(defaults.get("missing_section_counts"), dict):
        defaults["missing_section_counts"] = {}
    defaults["total_reviews"] = defaults.get(
        "total_reviews",
        defaults["total_reviews_submitted"],
    )
    defaults["total_score"] = defaults.get("total_score", defaults["audit_score_sum"])
    defaults["audit_runs"] = defaults.get("audit_runs", defaults["audit_score_count"])
    defaults["average_score"] = safe_average(
        defaults.get("total_score", 0.0),
        defaults.get("audit_runs", 0),
    )
    return defaults


def increment_runs() -> None:
    data = get_usage()
    data["total_runs"] += 1
    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def increment_reviews() -> None:
    data = get_usage()
    data["total_reviews_submitted"] += 1
    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def update_audit_metrics(audit_result: dict | None) -> None:
    if not audit_result or "error" in audit_result:
        return

    data = get_usage()
    data["audit_score_sum"] += audit_result.get("completeness_score", 0.0)
    data["audit_score_count"] += 1
    data["total_score"] = data["audit_score_sum"]
    data["audit_runs"] = data["audit_score_count"]
    data["average_score"] = safe_average(data["total_score"], data["audit_runs"])

    missing_counts = data.get("missing_section_counts", {})
    for item in audit_result.get("missing", []):
        missing_counts[item] = missing_counts.get(item, 0) + 1
    data["missing_section_counts"] = missing_counts

    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def mask_identifiers(text: str) -> str:
    if not text:
        return ""

    sanitized_lines = []
    for line in text.splitlines():
        stripped_line = line.strip()
        preserved_prefix = None
        working_line = line

        if stripped_line in SECTION_HEADER_ALLOWLIST:
            sanitized_lines.append(line)
            continue

        numbered_heading_match = re.match(r"^(\d+\.\s+)(.+)$", stripped_line)
        if numbered_heading_match and numbered_heading_match.group(2) in SECTION_HEADER_ALLOWLIST:
            sanitized_lines.append(line)
            continue

        if ":" in line:
            possible_header, remainder = line.split(":", 1)
            normalized_header = re.sub(r"^\d+\.\s+", "", possible_header.strip())
            if normalized_header in SECTION_HEADER_ALLOWLIST:
                preserved_prefix = possible_header.strip()
                working_line = remainder.lstrip()

        sanitized_line = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]", working_line)
        sanitized_line = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", sanitized_line)
        sanitized_line = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "[DOB]", sanitized_line)
        sanitized_line = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", sanitized_line)
        sanitized_line = re.sub(r"\b\d{5}(?:-\d{4})?\b", "[ZIP]", sanitized_line)
        sanitized_line = re.sub(
            r"\b\d{1,5}\s+[A-Za-z0-9\s]+\s(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Boulevard|Blvd)\b",
            "[ADDRESS]",
            sanitized_line,
            flags=re.IGNORECASE,
        )
        sanitized_line = re.sub(r"(Name:\s*)([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", r"\1[NAME]", sanitized_line)
        sanitized_line = re.sub(r"\b([A-Z][a-z]{2,}\s[A-Z][a-z]{2,})\b", "[NAME]", sanitized_line)
        sanitized_line = re.sub(r"\b\d{4,}\b", "[ID]", sanitized_line)
        if preserved_prefix:
            sanitized_line = f"{preserved_prefix}: {sanitized_line}" if sanitized_line else f"{preserved_prefix}:"
        sanitized_lines.append(sanitized_line)

    return "\n".join(sanitized_lines)


def sanitize_identifiers(text: str) -> str:
    return mask_identifiers(text)


def prepare_interaction_text(text: str) -> str:
    if st.session_state["ALLOW_PID"]:
        return text
    return sanitize_identifiers(text)


def sanitization_confidence_check(text: str) -> str:
    possible_names = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
    possible_ids = re.findall(r"\b\d{4,}\b", text)
    possible_email = re.search(r"@", text)

    score = 0
    if len(possible_names) > 5:
        score += 1
    if possible_ids:
        score += 1
    if possible_email:
        score += 2

    if score >= 2:
        return "LOW"
    if score == 1:
        return "MEDIUM"
    return "HIGH"


def qc_sanitization_check(text: str) -> dict:
    issues = []

    if "@" in text:
        issues.append("Possible email detected")
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
        issues.append("Possible SSN detected")
    if re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text):
        issues.append("Possible name detected")
    if re.search(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", text):
        issues.append("Possible phone detected")

    confidence = sanitization_confidence_check(text)
    return {
        "issues": issues,
        "confidence": confidence,
        "safe": len(issues) == 0 and confidence == "HIGH",
    }


def detect_flags(intake_text: str) -> list[str]:
    keywords = [
        "fall",
        "dizziness",
        "fainting",
        "medication",
        "blood thinner",
        "pregnant",
        "chest pain",
        "severe",
        "confusion",
        "emergency",
        "interaction",
        "allergy",
        "shortness of breath",
        "suicidal",
        "overdose",
    ]
    lowered = intake_text.lower() if intake_text else ""
    return sorted({keyword for keyword in keywords if keyword in lowered})


def detect_practitioner_triggers(intake_text: str, practitioner_type: str) -> list[str]:
    lower_text = intake_text.lower()
    found = []
    grouped_triggers = PRACTITIONER_TRIGGER_GROUPS.get(practitioner_type, [])

    for label, terms in grouped_triggers:
        if any(term in lower_text for term in terms):
            found.append(label)

    if found:
        return found

    knowledge = PRACTITIONER_KNOWLEDGE_MAP.get(practitioner_type, {})
    triggers = knowledge.get("trigger_terms", [])
    return [term for term in triggers if term.lower() in lower_text]


def detect_documentation_gaps(intake_text: str, practitioner_type: str) -> list[str]:
    knowledge = PRACTITIONER_KNOWLEDGE_MAP.get(practitioner_type, {})
    needs = knowledge.get("documentation_needs", [])
    gaps = []

    lower_text = intake_text.lower()

    for need in needs:
        if need.lower() not in lower_text:
            gaps.append(need)

    return gaps


def extract_attachment_text(uploaded_file) -> tuple[str, dict]:
    if not uploaded_file:
        return "", {
            "included": False,
            "filename": "None",
            "handling_type": "none",
            "ui_message": "",
        }

    filename = uploaded_file.name
    suffix = Path(filename).suffix.lower()
    metadata = {
        "included": True,
        "filename": filename,
        "handling_type": "none",
        "ui_message": "",
    }

    if suffix == ".pdf":
        metadata["handling_type"] = "pdf manual review"
        metadata["ui_message"] = "PDF attached - manual review recommended"
        return "", metadata

    try:
        attachment_text = uploaded_file.getvalue().decode("utf-8", errors="ignore").strip()
    except Exception:
        attachment_text = ""

    if attachment_text:
        metadata["handling_type"] = "text incorporated"
        return sanitize_identifiers(attachment_text), metadata

    metadata["handling_type"] = "none"
    return "", metadata


def list_saved_outputs() -> list[Path]:
    files = list(OUTPUTS_DIR.rglob("*.md")) if OUTPUTS_DIR.exists() else []
    return sorted(files, reverse=True)


def get_model():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY environment variable not set. Please set it in your environment or .env file.")
        return None

    if MODEL_PROVIDER == "openai":
        return OpenAIAdapter(model_name=MODEL_NAME, api_key=api_key)
    if MODEL_PROVIDER == "claude":
        return ClaudeAdapter()
    raise ValueError("Unsupported model")


def get_specialty_instruction(practitioner: str) -> str:
    if practitioner == "Occupational Therapist":
        return """
For OT documentation, prioritize:
- motor control
- proprioceptive input
- fatigue
- muscular weakness
- mobility deficits
- load tolerance
- body mechanics
- fall prevention
- injury avoidance
- home exercise program
- ADLs/IADLs
- functional independence
- work-related limitations when workers comp is mentioned

The output should connect:
findings -> deficits -> functional impact -> justification for skilled therapy -> intervention direction.
""".strip()

    if practitioner == "Nurse":
        return """
For nursing documentation, prioritize:
- medication amounts
- units
- route
- timing
- administration context
- monitoring needs
- patient safety concerns
- escalation criteria

Do not convert or calculate medication amounts unless the intake provides enough information and the output clearly states that professional verification is required.
""".strip()

    if practitioner == "Pharmacist":
        return """
For pharmacist review, prioritize:
- medication/supplement list completeness
- adherence
- interaction concern flags
- contraindication concern flags
- counseling questions
- escalation to pharmacist review when medication complexity is present
- request dose, frequency, route, timing, and a complete medication list when not provided

Do not make definitive interaction claims unless explicitly supported.
""".strip()

    if practitioner == "Wellness Consultant":
        return """
For wellness consulting, prioritize:
- goals
- preferences
- routines
- lifestyle constraints
- education needs
- gentle next steps
- escalation if safety or medication concerns appear

Avoid medical claims.
""".strip()

    return "Use conservative, reviewable language and escalate unclear or high-risk issues."


def build_system_prompt(
    practitioner: str,
    person_term_choice: str,
) -> str:
    if person_term_choice == "Auto":
        if practitioner in ["Pharmacist", "Nurse", "General Medical Reviewer", "Occupational Therapist"]:
            prof_term = "patient"
        elif practitioner == "Wellness Consultant":
            prof_term = "client"
        else:
            prof_term = "individual"
    else:
        prof_term = person_term_choice.lower()

    if USE_ASSIGNMENT_FORMAT:
        output_sections = """
Generate exactly these sections:
1. Findings
2. Assessment
3. Deficits
4. Functional Impact
5. Justification
6. Intervention
7. Suggested Next Actions
8. Individual-Facing Summary
9. QC Review
10. Review Status
""".strip()
    else:
        output_sections = """
Generate exactly these sections:
1. Original Intake Summary
2. Practitioner-Specific Triggers Detected
3. Assessment / Professional Interpretation
4. Identified Deficits or Concerns
5. Functional or Practical Impact
6. Justification for Intervention or Review
7. Suggested Next Actions
8. Individual-Facing Summary
9. QC Review Notes
10. Review Status
""".strip()

    pharmacist_guardrails = ""
    if practitioner == "Pharmacist":
        pharmacist_guardrails = """
For pharmacist outputs:
- Do NOT make definitive risk claims
- Use cautious phrasing such as: may warrant review, possible concern, requires pharmacist review
- Avoid implying confirmed interactions unless explicitly stated
- Always request dose, frequency, route, timing, and a complete medication list when they are not provided
- Do not recommend medication changes, discontinuation, or definitive clinical conclusions without pharmacist review
""".strip()

    return f"""
You are an expert {practitioner} documentation assistant.

You are not merely summarizing. You are assisting the practitioner by:
- preserving the meaning of the original intake
- identifying relevant practitioner-specific concepts
- mapping relevant intake details to accepted field terminology
- identifying documentation gaps
- drafting assessment language only when supported by the intake
- linking findings -> deficits -> functional impact -> justification -> intervention when appropriate
- clearly labeling system-added content
- avoiding unsupported diagnosis, treatment decisions, or definitive medical claims

Rules:
- Draft only. Human review required before use.
- No diagnosis.
- No final treatment decisions.
- No medication, supplement, or interaction claims unless clearly supported by the intake text.
- Escalate higher-risk concerns, including fall risk, severe symptoms, medication complexity, incomplete information, or unclear safety concerns.
- Use professional, natural language.
- Keep the individual-facing language gentle, supportive, and easy to understand.
- When details are missing, state the gap explicitly instead of filling it in.
- Do not introduce demographics, medications, diagnoses, allergies, supplements, assessments, or clinical facts that were not explicitly provided in the intake text or attachment.
- Use phrases such as not provided, requires clarification, or should be verified instead of inventing missing details.
- Make system-added interpretation reviewable and clearly supported by the intake.
- Use \"{prof_term}\" in the professional-facing note.
- Use second-person language (\"you\") in the individual-facing summary.

{pharmacist_guardrails}

{output_sections}

Review Status must be exactly one of:
- Standard Human Review
- Mandatory Human Review
""".strip()


def build_user_prompt(
    practitioner: str,
    tone: str,
    client_age: str,
    client_goals: str,
    current_meds: str,
    relevant_concerns: str,
    flags: list[str],
    intake_text: str,
    practitioner_context: dict,
    practitioner_triggers: list[str],
    documentation_gaps: list[str],
) -> str:
    specialty_instruction = get_specialty_instruction(practitioner)
    return f"""
Practitioner Type: {practitioner}
Preferred Tone: {tone}
Age: {client_age or 'Not provided'}
Goals or Main Concern: {client_goals or 'Not provided'}
Current Medications or Supplements: {current_meds or 'Not provided'}
Relevant Safety Concerns: {relevant_concerns or 'None provided'}
Detected Safety Flags: {', '.join(flags) if flags else 'None'}

Practitioner Focus:
{practitioner_context.get('focus', 'General review support')}

Detected Trigger Terms:
{', '.join(practitioner_triggers) if practitioner_triggers else 'None detected'}

Possible Documentation Gaps:
{', '.join(documentation_gaps) if documentation_gaps else 'No obvious gaps detected'}

Source Note:
{practitioner_context.get('source_note', 'Use conservative, reviewable language.')}

Review Reminder:
All additions must be reviewed by the practitioner before use.

Feedback-Informed Enhancement:
Be specific. If the intake is incomplete, name the missing details and explain why they matter for review rather than staying generic.

Specialty Instruction:
{specialty_instruction}

Intake Responses:
{intake_text.strip()}

If any detected safety flags are present, set Review Status to Mandatory Human Review.
""".strip()


def call_llm(system_prompt: str, user_prompt: str) -> tuple[str | None, str | None]:
    model = get_model()
    if not model:
        return None, "Missing API key."

    try:
        return model.generate(system_prompt, user_prompt), None
    except Exception as exc:
        return None, f"OpenAI API error: {exc}"


def save_output_local(
    practitioner_type: str,
    intake_text: str,
    detected_flags: list[str],
    practitioner_triggers: list[str],
    documentation_gaps: list[str],
    generated_output: str,
    reviewer_comments: str,
    review_status: str,
    review_outcome: str,
    review_complete: bool,
    attachment_metadata: dict,
    qc_summary: dict,
) -> Path:
    practitioner_dir = OUTPUTS_DIR / practitioner_type
    practitioner_dir.mkdir(parents=True, exist_ok=True)
    file_path = practitioner_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    content = f"""# {APP_NAME} Output

## Metadata
- Saved At: {datetime.now().isoformat(timespec='seconds')}
- Product: {APP_NAME}
- Product Tagline: {APP_TAGLINE}
- Copyright: {COPYRIGHT_NOTICE}
- Practitioner Type: {practitioner_type}
- Review Status: {review_status}
- Review Outcome: {review_outcome}
- Review Completion Status: {'Complete' if review_complete else 'Incomplete'}

## Ownership Notice
{COPYRIGHT_NOTICE}

{DRAFTSAFE_OWNERSHIP_NOTICE}

## Attachment Metadata
- Attachment Included: {'Yes' if attachment_metadata['included'] else 'No'}
- Filename: {attachment_metadata['filename']}
- Handling Type: {attachment_metadata['handling_type']}

## Intake Text (Sanitized)
[{intake_text}]

## Detected Flags
{', '.join(detected_flags) if detected_flags else 'None'}

## Practitioner-Specific Triggers
{', '.join(practitioner_triggers) if practitioner_triggers else 'None'}

## Possible Documentation Gaps
{', '.join(documentation_gaps) if documentation_gaps else 'None'}

## Generated Output (Sanitized)
{generated_output}

## Reviewer Comments
{reviewer_comments or 'None'}

## QC Summary
- QC Safe: {qc_summary['qc_safe']}
- Issues Detected: {qc_summary['issues_detected'] if qc_summary['issues_detected'] else 'None'}

## Sanitization / QC Summary
- Input Confidence: {qc_summary['input_confidence']}
- Output Confidence: {qc_summary['output_confidence']}
- Reviewer Comments Confidence: {qc_summary['comments_confidence']}
- Input Issues: {', '.join(qc_summary['input_issues']) if qc_summary['input_issues'] else 'None'}
- Output Issues: {', '.join(qc_summary['output_issues']) if qc_summary['output_issues'] else 'None'}
- Reviewer Comment Issues: {', '.join(qc_summary['comments_issues']) if qc_summary['comments_issues'] else 'None'}
- Safe to Store After Sanitization: {'Yes' if qc_summary['safe_to_store_after_sanitization'] else 'No'}

## Reminder
Draft only. Requires human review before use.

## DraftSafe™ Ownership & Use Notice

{COPYRIGHT_NOTICE}

DraftSafe™ is an independently developed educational and workflow-support prototype.

This system assists with intake organization, AI-assisted draft generation, deterministic documentation auditing, and practitioner review support but does not replace licensed professional judgment.

No portion of this workflow, generated structure, audit methodology, or implementation may be reproduced or commercialized without written permission from the author.
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def save_output_cloud(
    practitioner_type: str,
    intake_text: str,
    detected_flags: list[str],
    practitioner_triggers: list[str],
    documentation_gaps: list[str],
    generated_output: str,
    reviewer_comments: str,
    review_status: str,
    review_outcome: str,
    review_complete: bool,
    attachment_metadata: dict,
    qc_summary: dict,
) -> None:
    _ = (
        practitioner_type,
        intake_text,
        detected_flags,
        practitioner_triggers,
        documentation_gaps,
        generated_output,
        reviewer_comments,
        review_status,
        review_outcome,
        review_complete,
        attachment_metadata,
        qc_summary,
    )
    # Placeholder for future cloud storage. Only sanitized data may be passed here.


def save_output(
    practitioner_type: str,
    intake_text: str,
    detected_flags: list[str],
    practitioner_triggers: list[str],
    documentation_gaps: list[str],
    generated_output: str,
    reviewer_comments: str,
    review_status: str,
    review_outcome: str,
    review_complete: bool,
    attachment_metadata: dict,
    qc_summary: dict,
) -> Path:
    sanitized_intake_text = sanitize_identifiers(intake_text)
    sanitized_generated_output = sanitize_identifiers(generated_output)
    sanitized_reviewer_comments = sanitize_identifiers(reviewer_comments)
    sanitized_attachment_metadata = {
        "included": attachment_metadata.get("included", False),
        "filename": sanitize_identifiers(attachment_metadata.get("filename", "None")) or "None",
        "handling_type": attachment_metadata.get("handling_type", "none"),
    }

    local_path = save_output_local(
        practitioner_type=practitioner_type,
        intake_text=sanitized_intake_text,
        detected_flags=detected_flags,
        practitioner_triggers=practitioner_triggers,
        documentation_gaps=documentation_gaps,
        generated_output=sanitized_generated_output,
        reviewer_comments=sanitized_reviewer_comments,
        review_status=review_status,
        review_outcome=review_outcome,
        review_complete=review_complete,
        attachment_metadata=sanitized_attachment_metadata,
        qc_summary=qc_summary,
    )
    save_output_cloud(
        practitioner_type=practitioner_type,
        intake_text=sanitized_intake_text,
        detected_flags=detected_flags,
        practitioner_triggers=practitioner_triggers,
        documentation_gaps=documentation_gaps,
        generated_output=sanitized_generated_output,
        reviewer_comments=sanitized_reviewer_comments,
        review_status=review_status,
        review_outcome=review_outcome,
        review_complete=review_complete,
        attachment_metadata=sanitized_attachment_metadata,
        qc_summary=qc_summary,
    )
    return local_path


initialize_usage()
if not st.session_state["run_incremented"]:
    increment_runs()
    st.session_state["run_incremented"] = True

st.markdown(
    """
    <style>
    .draftsafe-header-card {
        display: flex;
        align-items: flex-start;
        margin: 0 0 0.7rem 0;
        padding: 0.85rem 1rem;
        background: #f5f7fa;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    }
    .draftsafe-brand-row {
        display: flex;
        align-items: flex-start;
        gap: 0.18rem;
        width: 100%;
    }
    .draftsafe-logo {
        width: 54px;
        min-width: 54px;
        height: auto;
        border-radius: 8px;
        margin: 0.12rem 0.5rem 0 0;
        display: block;
    }
    .draftsafe-copy-wrap {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        min-width: 0;
    }
    .draftsafe-title-row {
        display: flex;
        align-items: baseline;
    }
    .draftsafe-title {
        margin: 0;
        color: #333333;
        font-size: 2.28rem;
        font-weight: 700;
        line-height: 1.02;
        letter-spacing: -0.02em;
    }
    .draftsafe-tagline {
        margin: 0.18rem 0 0 0;
        color: #5a5a5a;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.2;
    }
    .draftsafe-subtitle {
        margin: 0.16rem 0 0 0;
        color: #7a7a7a;
        font-size: 0.9rem;
        line-height: 1.28;
    }
    .draftsafe-review-badge {
        display: inline-block;
        margin: 0.35rem 0 0.4rem 0;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        background: #eef2f7;
        border: 1px solid #d8dee8;
        color: #334155;
        font-size: 0.84rem;
        font-weight: 600;
        letter-spacing: 0.01em;
    }
    .draftsafe-review-box {
        margin-top: 0.5rem;
        padding: 0.8rem 0.9rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
    }
    .draftsafe-review-box-title {
        margin: 0 0 0.4rem 0;
        color: #334155;
        font-size: 0.95rem;
        font-weight: 600;
    }
    .draftsafe-review-box ul {
        margin: 0;
        padding-left: 1.1rem;
        color: #475569;
    }
    .draftsafe-review-box li {
        margin: 0.18rem 0;
    }
    .draftsafe-list-box {
        margin-top: 0.35rem;
        padding: 0.8rem 0.9rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
    }
    .draftsafe-list-box ul {
        margin: 0;
        padding-left: 1.1rem;
        color: #475569;
    }
    .draftsafe-list-box li {
        margin: 0.18rem 0;
    }
    @media (prefers-color-scheme: dark) {
        .draftsafe-header-card {
            background: rgba(17, 24, 39, 0.92);
            border-color: rgba(148, 163, 184, 0.18);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22);
        }
        .draftsafe-title {
            color: #f8fafc;
        }
        .draftsafe-tagline {
            color: #e2e8f0;
        }
        .draftsafe-subtitle {
            color: #cbd5e1;
        }
        .draftsafe-review-badge {
            background: rgba(51, 65, 85, 0.7);
            border-color: rgba(148, 163, 184, 0.22);
            color: #e2e8f0;
        }
        .draftsafe-review-box {
            background: rgba(15, 23, 42, 0.52);
            border-color: rgba(148, 163, 184, 0.18);
        }
        .draftsafe-review-box-title {
            color: #e2e8f0;
        }
        .draftsafe-review-box ul {
            color: #cbd5e1;
        }
        .draftsafe-list-box {
            background: rgba(15, 23, 42, 0.52);
            border-color: rgba(148, 163, 184, 0.18);
        }
        .draftsafe-list-box ul {
            color: #cbd5e1;
        }
    }
    @media (max-width: 768px) {
        .draftsafe-header-card {
            padding: 0.7rem 0.75rem;
            border-radius: 14px;
        }
        .draftsafe-brand-row {
            gap: 0.1rem;
        }
        .draftsafe-logo {
            width: 44px;
            min-width: 44px;
            margin: 0.08rem 0.4rem 0 0;
        }
        .draftsafe-title {
            font-size: 1.72rem;
        }
        .draftsafe-tagline {
            font-size: 0.92rem;
        }
        .draftsafe-subtitle {
            font-size: 0.82rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_markup = ""
if APP_LOGO_BASE64:
    logo_markup = f'<img class="draftsafe-logo" src="data:image/png;base64,{APP_LOGO_BASE64}" alt="DraftSafe logo" />'

st.markdown(
    f"""
    <div class="draftsafe-header-card">
        <div class="draftsafe-brand-row">
            {logo_markup}
            <div class="draftsafe-copy-wrap">
                <div class="draftsafe-title-row">
                    <div class="draftsafe-title">{APP_NAME}</div>
                </div>
                <div class="draftsafe-tagline">{APP_TAGLINE}</div>
                <div class="draftsafe-subtitle">{APP_SUBTITLE}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

usage = get_usage()
IS_ADMIN = False

with st.sidebar:
    st.markdown(f"### {APP_NAME}")
    st.caption(APP_TAGLINE)
    st.header("Privacy and Safety Notes")
    st.markdown(
        """
        - Use synthetic or non-identifying data for testing
        - **Do not enter real patient-identifying information**
        - Outputs are drafts and require human review
        - High-risk cases should not be handled automatically
        - This app is not intended for diagnosis or autonomous treatment decisions
        """
    )

    st.subheader("Privacy Controls")
    audit_enabled = st.checkbox(
        "Enable Documentation Audit",
        value=True,
        help="Runs a deterministic keyword-based completeness check after draft generation.",
    )
    st.selectbox(
        "Model (future)",
        ["openai", "claude"],
        disabled=True,
    )
    admin_key = st.text_input("Admin Key", type="password")
    IS_ADMIN = admin_key == "admin123"
    if IS_ADMIN:
        st.session_state["ALLOW_PID"] = st.checkbox(
            "Allow identifiers (admin only)",
            value=st.session_state["ALLOW_PID"],
        )
    else:
        st.session_state["ALLOW_PID"] = False
        st.caption("Enter the admin key to enable identifier passthrough for controlled testing.")

    allow_pid = st.session_state["ALLOW_PID"]
    if allow_pid:
        st.info(
            "Identifiers may be visible during use, but all saved outputs are automatically sanitized."
        )
    else:
        st.success("Identifier protection active")
    st.caption(
        f"Identifier Protection: {'OFF (Identifiers Allowed)' if allow_pid else 'ON (Identifiers Masked)'}"
    )

    st.subheader("Usage Dashboard")
    total_app_runs = safe_dashboard_value(usage.get("total_runs"), 0)
    total_reviews_submitted = safe_dashboard_value(usage.get("total_reviews_submitted"), 0)
    average_audit_score = safe_average(
        usage.get("audit_score_sum", 0.0),
        usage.get("audit_score_count", 0),
    )
    average_audit_score_display = safe_dashboard_value(f"{average_audit_score:.2f}", 0)

    if usage.get("missing_section_counts"):
        most_common_missing = max(
            usage["missing_section_counts"],
            key=usage["missing_section_counts"].get,
        )
    else:
        most_common_missing = "None recorded yet"

    st.metric("Total App Runs", total_app_runs)
    st.metric("Reviews Submitted", total_reviews_submitted)
    st.metric("Avg Audit Score", average_audit_score_display)
    st.caption(
        f"Most common missing section: {safe_dashboard_value(most_common_missing)}"
    )
    if usage.get("audit_score_count", 0) == 0 and usage.get("total_reviews_submitted", 0) == 0:
        st.info("Dashboard analytics will populate as reviews and audits are completed.")
    st.info(f"Join the test group — {total_reviews_submitted} reviews completed so far.")

st.warning("All identifiers are automatically removed and replaced with placeholders unless explicitly enabled.")
st.warning("All outputs must be reviewed. Identifier sanitization is not guaranteed to be perfect.")
st.info(
    "All outputs are automatically sanitized before saving. No identifiers are ever stored, regardless of settings."
)
st.info(
    "Outputs are private to your session. Saved outputs are not visible to other users."
)

if not IS_ADMIN:
    st.info("Session mode: Only your generated output is visible.")

if st.button("Clear Session"):
    st.session_state.clear()
    st.rerun()

if st.session_state["save_success_message"]:
    st.success(st.session_state["save_success_message"])
    if st.session_state["save_success_path"]:
        st.caption(f"Saved file: {st.session_state['save_success_path']}")
    st.session_state["save_success_message"] = ""
    st.session_state["save_success_path"] = ""
if st.session_state["save_incomplete_warning"]:
    st.warning(st.session_state["save_incomplete_warning"])
    st.session_state["save_incomplete_warning"] = ""

practitioner = st.selectbox(
    "Practitioner Type",
    [
        "Pharmacist",
        "Nurse",
        "Wellness Consultant",
        "Occupational Therapist",
        "General Medical Reviewer",
    ],
)
person_term_choice = st.selectbox(
    "Person-Facing Terminology",
    ["Auto", "Patient", "Client", "Individual"],
    help="Controls the label used in the professional-facing note. The individual-facing summary still uses second-person language.",
)
intake_text = st.text_area("Paste Intake Form Responses", height=220)
attachment = st.file_uploader(
    "Attach intake form or supporting notes (optional)",
    type=["txt", "md", "csv", "pdf"],
)
st.caption("Use synthetic or non-identifying data for testing.")

col1, col2 = st.columns(2)
with col1:
    client_age = st.text_input("Client Age (optional)")
    client_goals = st.text_input("Goals or Main Concern (optional)")
with col2:
    current_meds = st.text_input("Current Medications or Supplements (optional)")
    relevant_concerns = st.text_input("Relevant Safety Concerns (optional)")

tone = "Gentle"
st.caption("Tone is automatically set to a gentle, patient-facing style for the individual-facing output.")

if st.button("Generate Draft"):
    raw_input = intake_text.strip()
    attachment_text, attachment_metadata = extract_attachment_text(attachment)
    if not raw_input and not attachment_text:
        if attachment_metadata.get("handling_type") == "pdf manual review":
            st.warning("PDF attached - manual review recommended. Please also provide intake text.")
        else:
            st.warning("Please enter intake form responses or attach a text-based intake file.")
    else:
        combined_raw_input = raw_input or attachment_text
        if raw_input and attachment_text:
            combined_raw_input = (
                f"{raw_input}\n\nAttached Intake/Form Content:\n{attachment_text}"
            )

        model_input = prepare_interaction_text(combined_raw_input)
        sanitized_input = sanitize_identifiers(combined_raw_input)
        detected_flags = detect_flags(model_input)
        practitioner_triggers = detect_practitioner_triggers(sanitized_input, practitioner)
        documentation_gaps = detect_documentation_gaps(sanitized_input, practitioner)
        practitioner_context = PRACTITIONER_KNOWLEDGE_MAP.get(practitioner, {})

        if attachment_metadata["ui_message"]:
            st.info(attachment_metadata["ui_message"])

        if detected_flags:
            st.error("Potential safety flags detected. Mandatory human review recommended.")
        else:
            st.info("No automatic safety flags detected. Standard human review still required.")

        system_prompt = build_system_prompt(
            practitioner=practitioner,
            person_term_choice=person_term_choice,
        )
        user_prompt = build_user_prompt(
            practitioner=practitioner,
            tone=tone,
            client_age=client_age,
            client_goals=client_goals,
            current_meds=current_meds,
            relevant_concerns=relevant_concerns,
            flags=detected_flags,
            intake_text=model_input,
            practitioner_context=practitioner_context,
            practitioner_triggers=practitioner_triggers,
            documentation_gaps=documentation_gaps,
        )

        with st.spinner("Generating draft..."):
            generated_output, error_message = call_llm(system_prompt, user_prompt)

        if error_message:
            st.error(error_message)
        elif generated_output:
            audit_result = None
            audit_message = ""
            audit_supported = practitioner.lower() in [
                "occupational therapist",
                "pharmacist",
            ]
            if audit_enabled and audit_supported:
                audit_result = audit_clinical_note(generated_output, practitioner)
                if "error" in audit_result:
                    audit_result = None
                    audit_message = "Audit not available for selected practitioner type."
            elif audit_enabled:
                audit_message = "Audit not available for selected practitioner type."

            st.session_state["last_intake_text"] = raw_input
            st.session_state["generated_output"] = generated_output
            interactive_output = prepare_interaction_text(generated_output)
            final_sanitized_input = sanitize_identifiers(combined_raw_input)
            final_sanitized_output = sanitize_identifiers(generated_output)
            qc_input = qc_sanitization_check(final_sanitized_input)
            qc_output = qc_sanitization_check(final_sanitized_output)

            st.session_state["draft_data"] = {
                "practitioner": practitioner,
                "person_term_choice": person_term_choice,
                "raw_input": raw_input,
                "combined_raw_input": combined_raw_input,
                "detected_flags": detected_flags,
                "practitioner_triggers": practitioner_triggers,
                "documentation_gaps": documentation_gaps,
                "raw_output": generated_output,
                "interactive_output": interactive_output,
                "final_sanitized_input": final_sanitized_input,
                "final_sanitized_output": final_sanitized_output,
                "qc_input": qc_input,
                "qc_output": qc_output,
                "confidence": qc_output["confidence"],
                "audit_enabled": audit_enabled,
                "audit_result": audit_result,
                "audit_message": audit_message,
                "attachment_metadata": attachment_metadata,
            }
        else:
            st.error("No output generated.")

draft_data = st.session_state.get("draft_data")

if draft_data:
    if "generated_output" in st.session_state:
        st.subheader("Generated Output")
        st.text_area("Output", st.session_state["generated_output"], height=300)

    practitioner_trigger_items = draft_data["practitioner_triggers"]
    documentation_gap_items = draft_data["documentation_gaps"]

    st.subheader("Practitioner-Specific Triggers")
    st.caption(f"Detected {len(practitioner_trigger_items)} practitioner-relevant cues")
    if practitioner_trigger_items:
        trigger_markup = "".join(f"<li>{item}</li>" for item in practitioner_trigger_items)
        st.markdown(
            f"""
            <div class="draftsafe-list-box">
                <ul>{trigger_markup}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption("No practitioner-specific triggers detected.")

    st.subheader("Possible Documentation Gaps")
    if documentation_gap_items:
        gap_markup = "".join(f"<li>{item}</li>" for item in documentation_gap_items)
        st.markdown(
            f"""
            <div class="draftsafe-list-box">
                <ul>{gap_markup}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption("No obvious gaps detected.")

    if draft_data.get("attachment_metadata", {}).get("included"):
        st.subheader("Attachment Metadata")
        st.write(
            {
                "Filename": draft_data["attachment_metadata"].get("filename", "None"),
                "Handling Type": draft_data["attachment_metadata"].get("handling_type", "none"),
            }
        )
        if draft_data["attachment_metadata"].get("handling_type") == "pdf manual review":
            st.info("PDF attached - manual review recommended")

    st.subheader("Documentation Audit")
    if draft_data.get("audit_enabled"):
        audit_result = draft_data.get("audit_result")
        if audit_result:
            completeness_percent = int(round(audit_result["completeness_score"] * 100))
            missing_sections = audit_result.get("review_areas", audit_result["missing"])
            found_sections = audit_result["found"]
            practitioner_metric_value = {
                "Occupational Therapist": "OT",
                "Pharmacist": "Pharm.",
                "Wellness Consultant": "Wellness",
                "General Medical Reviewer": "Reviewer",
            }.get(draft_data["practitioner"], draft_data["practitioner"])
            audit_review_status = audit_result.get("review_status", "")
            if draft_data["detected_flags"] or audit_review_status == "Mandatory Human Review":
                review_badge = "Human Review Required"
                review_metric_value = "Required"
            elif missing_sections or audit_review_status == "Additional Review Suggested":
                review_badge = "Additional Review Suggested"
                review_metric_value = "Suggested"
            else:
                review_badge = "Draft Ready for Review"
                review_metric_value = "Ready"

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            metric_col1.metric("Practitioner Type", practitioner_metric_value)
            metric_col2.metric("Completeness", f"{completeness_percent}%")
            metric_col3.metric("Missing Sections", str(len(missing_sections)))
            metric_col4.metric("Review Status", review_metric_value)

            st.caption(f"Documentation Checks for {draft_data['practitioner']}")
            st.caption(f"Documentation Completeness: {completeness_percent}%")
            st.progress(completeness_percent)
            st.markdown(
                f'<div class="draftsafe-review-badge">{review_badge}</div>',
                unsafe_allow_html=True,
            )
            st.write(
                "Found:",
                found_sections if found_sections else "None detected",
            )
            st.write(
                "Missing:",
                missing_sections if missing_sections else "None detected",
            )
            if missing_sections:
                review_area_items = "".join(
                    f"<li>{item[:1].upper() + item[1:]}</li>" for item in missing_sections
                )
                st.markdown(
                    f"""
                    <div class="draftsafe-review-box">
                        <div class="draftsafe-review-box-title">Detected Review Areas</div>
                        <ul>{review_area_items}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.warning(
                    "Some documentation details may still need review before finalizing."
                )
        else:
            st.caption(draft_data.get("audit_message") or "Audit not available for selected practitioner type.")
    else:
        st.caption("Documentation audit is disabled for this draft.")

    st.subheader("System-Added Content (Review Required)")
    st.info("System-added content must be reviewed by the practitioner before use.")

    st.subheader("Detected Flags")
    if draft_data["detected_flags"]:
        st.write(", ".join(draft_data["detected_flags"]))
    else:
        st.write("None")

    qc_input = draft_data["qc_input"]
    qc_output = draft_data["qc_output"]
    qc_safe = qc_input["safe"] and qc_output["safe"]
    confidence = draft_data["confidence"]

    st.subheader("Sanitization Confidence")
    if confidence == "HIGH":
        st.success("High confidence: identifiers likely removed")
    elif confidence == "MEDIUM":
        st.warning("Medium confidence: review for possible missed identifiers")
    else:
        st.error("Low confidence: potential identifiers remain, manual review required")

    st.subheader("Sanitization QC Check")
    if qc_safe:
        st.success("QC Passed: No identifiers detected")
    else:
        st.warning("QC Warning: Potential identifiers were detected and removed before saving.")
        st.write("Detected issues:", qc_input["issues"] + qc_output["issues"])

    review_status_default = (
        "Mandatory Human Review"
        if draft_data["detected_flags"]
        or draft_data.get("audit_result", {}).get("review_status") == "Mandatory Human Review"
        else "Standard Human Review"
    )
    current_review_status = st.session_state.get("review_status_select")
    if current_review_status not in {"Standard Human Review", "Mandatory Human Review"}:
        st.session_state["review_status_select"] = review_status_default
    elif (
        review_status_default == "Mandatory Human Review"
        and current_review_status != "Mandatory Human Review"
    ):
        st.session_state["review_status_select"] = "Mandatory Human Review"

    review_status = st.selectbox(
        "Review Status",
        ["Standard Human Review", "Mandatory Human Review"],
        index=0 if review_status_default == "Standard Human Review" else 1,
        key="review_status_select",
    )
    review_outcome = st.selectbox(
        "Review Outcome",
        [
            "Pending Reviewer Decision",
            "Approved as Draft",
            "Needs Revision",
            "Escalated for Further Review",
        ],
        key="review_outcome_select",
    )
    review_complete = st.checkbox("Review Complete", key="review_complete_checkbox")
    st.caption(
        "Suggested reviewer prompt: Did the output correctly connect findings, deficits, justification, and next actions?"
    )
    reviewer_comments = st.text_area("Reviewer Comments", key="reviewer_comments")

    if st.button("Submit Review and Save"):
        sanitized_input = sanitize_identifiers(draft_data.get("combined_raw_input", st.session_state["last_intake_text"]))
        sanitized_output = sanitize_identifiers(st.session_state["generated_output"])
        sanitized_comments = sanitize_identifiers(reviewer_comments)

        sanitized_input = sanitize_identifiers(sanitized_input)
        sanitized_output = sanitize_identifiers(sanitized_output)
        sanitized_comments = sanitize_identifiers(sanitized_comments)

        qc_input = qc_sanitization_check(sanitized_input)
        qc_output = qc_sanitization_check(sanitized_output)
        qc_comments = qc_sanitization_check(sanitized_comments)
        qc_safe = qc_input["safe"] and qc_output["safe"] and qc_comments["safe"]

        if st.session_state["ALLOW_PID"]:
            st.info(
                "Identifiers may be visible during use, but all saved outputs are automatically sanitized."
            )

        if qc_safe:
            st.success("QC Passed: No identifiers detected")
        else:
            st.warning("QC Warning: Potential identifiers were detected and removed before saving.")
            st.write("Detected issues:", qc_input["issues"] + qc_output["issues"])

        qc_summary = {
            "qc_safe": qc_safe,
            "issues_detected": ", ".join(qc_input["issues"] + qc_output["issues"]),
            "input_confidence": qc_input["confidence"],
            "output_confidence": qc_output["confidence"],
            "comments_confidence": qc_comments["confidence"],
            "input_issues": qc_input["issues"],
            "output_issues": qc_output["issues"],
            "comments_issues": qc_comments["issues"],
            "safe_to_store_after_sanitization": True,
        }

        saved_path = save_output(
            practitioner_type=draft_data["practitioner"],
            intake_text=sanitized_input,
            detected_flags=draft_data["detected_flags"],
            practitioner_triggers=draft_data["practitioner_triggers"],
            documentation_gaps=draft_data["documentation_gaps"],
            generated_output=sanitized_output,
            reviewer_comments=sanitized_comments,
            review_status=review_status,
            review_outcome=review_outcome,
            review_complete=review_complete,
            attachment_metadata=draft_data.get("attachment_metadata", {}),
            qc_summary=qc_summary,
        )
        increment_reviews()
        update_audit_metrics(draft_data.get("audit_result"))
        st.session_state["save_success_message"] = "Output saved successfully (sanitized)."
        st.session_state["save_success_path"] = saved_path.name
        if not review_complete:
                st.session_state["save_incomplete_warning"] = "Output saved, but review was marked incomplete."
        st.rerun()

if IS_ADMIN:
    st.subheader("Admin Dashboard")
    try:
        files = list_saved_outputs()
    except Exception:
        files = []

    if files:
        selected_file = st.selectbox(
            "Select saved output",
            [file.name for file in files],
        )

        selected_path = next(file for file in files if file.name == selected_file)
        content = selected_path.read_text(encoding="utf-8")

        st.text_area("Saved Output", content, height=300)
    else:
        st.info("No saved outputs yet.")

st.divider()
for footer_line in APP_FOOTER_LINES:
    st.caption(footer_line)
st.caption(DRAFTSAFE_OWNERSHIP_NOTICE)
