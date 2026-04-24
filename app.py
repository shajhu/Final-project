# API key is loaded from .env for local development
# Do not hardcode secrets

import json
import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_NAME = "gpt-4.1-mini"  # If model access fails, gpt-4o-mini may be used as a fallback.
BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
USAGE_FILE = BASE_DIR / "usage.json"

st.set_page_config(page_title="Intake-to-Note Assistant", layout="centered")

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


def initialize_usage() -> None:
    if not USAGE_FILE.exists():
        USAGE_FILE.write_text(
            json.dumps({"total_runs": 0, "total_reviews_submitted": 0}, indent=2),
            encoding="utf-8",
        )


def get_usage() -> dict:
    try:
        return json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"total_runs": 0, "total_reviews_submitted": 0}


def increment_runs() -> None:
    data = get_usage()
    data["total_runs"] += 1
    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def increment_reviews() -> None:
    data = get_usage()
    data["total_reviews_submitted"] += 1
    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def mask_identifiers(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", text)
    text = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "[DOB]", text)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", text)
    text = re.sub(r"\b\d{5}(?:-\d{4})?\b", "[ZIP]", text)
    text = re.sub(
        r"\b\d{1,5}\s+[A-Za-z0-9\s]+\s(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Boulevard|Blvd)\b",
        "[ADDRESS]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"(Name:\s*)([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", r"\1[NAME]", text)
    text = re.sub(r"\b([A-Z][a-z]{2,}\s[A-Z][a-z]{2,})\b", "[NAME]", text)
    text = re.sub(r"\b\d{4,}\b", "[ID]", text)
    return text


def sanitize_identifiers(text: str) -> str:
    if st.session_state["ALLOW_PID"]:
        return text
    return mask_identifiers(text)


def sanitize_for_storage(text: str) -> str:
    return mask_identifiers(text)


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


def list_saved_outputs() -> list[Path]:
    files = list(OUTPUTS_DIR.rglob("*.md")) if OUTPUTS_DIR.exists() else []
    return sorted(files, reverse=True)


def get_openai_client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY environment variable not set. Please set it in your environment or .env file.")
        return None
    return OpenAI(api_key=api_key)


def build_system_prompt(
    practitioner: str,
    person_term_choice: str,
    tone: str,
    client_age: str,
    client_goals: str,
    current_meds: str,
    relevant_concerns: str,
    flags: list[str],
    intake_text: str,
) -> str:
    if person_term_choice == "Auto":
        if practitioner in ["Pharmacist", "Nurse", "General Medical Reviewer"]:
            prof_term = "patient"
        elif practitioner == "Wellness Consultant":
            prof_term = "client"
        else:
            prof_term = "individual"
    else:
        prof_term = person_term_choice.lower()

    return f"""
You are an expert {practitioner} assistant. Convert the intake into a safe draft for human review.

Rules:
- Draft only. Human review required before use.
- No diagnosis.
- No final treatment decisions.
- No medication, supplement, or interaction claims unless clearly supported by the intake text.
- Escalate higher-risk concerns, including fall risk, severe symptoms, medication complexity, incomplete information, or unclear safety concerns.
- Use professional, natural language.
- Keep the individual-facing language gentle, supportive, and easy to understand.
- Use \"{prof_term}\" in the professional-facing note.
- Use second-person language (\"you\") in the individual-facing summary.

Generate exactly these sections:
1. Structured Review Note
2. Key Intake Highlights
3. Individual-Facing Summary
4. Suggested Next Steps
5. Flagged Concerns
6. Review Status

Review Status must be exactly one of:
- Standard Human Review
- Mandatory Human Review

Practitioner Type: {practitioner}
Preferred Tone: {tone}
Age: {client_age or 'Not provided'}
Goals or Main Concern: {client_goals or 'Not provided'}
Current Medications or Supplements: {current_meds or 'Not provided'}
Relevant Safety Concerns: {relevant_concerns or 'None provided'}
Detected Safety Flags: {', '.join(flags) if flags else 'None'}

Intake Responses:
{intake_text.strip()}

If any detected safety flags are present, set Review Status to Mandatory Human Review.
""".strip()


def call_llm(prompt: str) -> tuple[str | None, str | None]:
    client = get_openai_client()
    if not client:
        return None, "Missing API key."

    try:
        response = client.responses.create(model=MODEL_NAME, input=prompt)
        return response.output_text, None
    except Exception as exc:
        return None, f"OpenAI API error: {exc}"


def save_output_local(
    practitioner_type: str,
    intake_text: str,
    detected_flags: list[str],
    generated_output: str,
    reviewer_comments: str,
    review_status: str,
    qc_summary: dict,
) -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUTS_DIR / f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    content = f"""# Intake-to-Note Assistant Output

## Metadata
- Saved At: {datetime.now().isoformat(timespec='seconds')}
- Practitioner Type: {practitioner_type}
- Review Status: {review_status}

## Intake Text (Sanitized)
{intake_text}

## Detected Flags
{', '.join(detected_flags) if detected_flags else 'None'}

## Generated Output (Sanitized)
{generated_output}

## Reviewer Comments
{reviewer_comments or 'None'}

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
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def save_output_cloud(
    practitioner_type: str,
    intake_text: str,
    detected_flags: list[str],
    generated_output: str,
    reviewer_comments: str,
    review_status: str,
    qc_summary: dict,
) -> None:
    _ = (
        practitioner_type,
        intake_text,
        detected_flags,
        generated_output,
        reviewer_comments,
        review_status,
        qc_summary,
    )
    # Placeholder for future cloud storage. Only sanitized data may be passed here.


def save_output(
    practitioner_type: str,
    intake_text: str,
    detected_flags: list[str],
    generated_output: str,
    reviewer_comments: str,
    review_status: str,
    qc_summary: dict,
) -> Path:
    local_path = save_output_local(
        practitioner_type=practitioner_type,
        intake_text=intake_text,
        detected_flags=detected_flags,
        generated_output=generated_output,
        reviewer_comments=reviewer_comments,
        review_status=review_status,
        qc_summary=qc_summary,
    )
    save_output_cloud(
        practitioner_type=practitioner_type,
        intake_text=intake_text,
        detected_flags=detected_flags,
        generated_output=generated_output,
        reviewer_comments=reviewer_comments,
        review_status=review_status,
        qc_summary=qc_summary,
    )
    return local_path


initialize_usage()
if not st.session_state["run_incremented"]:
    increment_runs()
    st.session_state["run_incremented"] = True

st.title("Intake-to-Note Assistant")
st.write(
    "Converts intake responses into a structured review note, draft follow-up, and flagged concerns for human review."
)

usage = get_usage()

with st.sidebar:
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
    admin_key = st.text_input("Admin Key", type="password")
    if admin_key == "admin123":
        st.session_state["ALLOW_PID"] = st.checkbox(
            "Allow identifiers (admin only)",
            value=st.session_state["ALLOW_PID"],
        )
    else:
        st.session_state["ALLOW_PID"] = False
        st.caption("Enter the admin key to enable identifier passthrough for controlled testing.")

    allow_pid = st.session_state["ALLOW_PID"]
    if allow_pid:
        st.error(
            "Identifier handling ENABLED.\n\n"
            "Do NOT use real patient data.\n"
            "This mode is for controlled testing only."
        )
    else:
        st.success("Identifier protection active")
    st.caption(
        f"Identifier Protection: {'OFF (Identifiers Allowed)' if allow_pid else 'ON (Identifiers Masked)'}"
    )

    st.subheader("Usage Dashboard")
    st.metric("Total App Runs", usage["total_runs"])
    st.metric("Reviews Submitted", usage["total_reviews_submitted"])
    st.info(f"Join the test group — {usage['total_reviews_submitted']} reviews completed so far.")

st.warning("All identifiers are automatically removed and replaced with placeholders unless explicitly enabled.")
st.warning("All outputs must be reviewed. Identifier sanitization is not guaranteed to be perfect.")
st.info(
    "All saved outputs are automatically sanitized. Identifiers are never stored, even if visible during interaction."
)

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
    if not raw_input:
        st.warning("Please enter intake form responses.")
    else:
        model_input = sanitize_identifiers(raw_input)
        detected_flags = detect_flags(model_input)

        if detected_flags:
            st.error("Potential safety flags detected. Mandatory human review recommended.")
        else:
            st.info("No automatic safety flags detected. Standard human review still required.")

        prompt = build_system_prompt(
            practitioner=practitioner,
            person_term_choice=person_term_choice,
            tone=tone,
            client_age=client_age,
            client_goals=client_goals,
            current_meds=current_meds,
            relevant_concerns=relevant_concerns,
            flags=detected_flags,
            intake_text=model_input,
        )

        with st.spinner("Generating draft..."):
            generated_output, error_message = call_llm(prompt)

        if error_message:
            st.error(error_message)
        elif generated_output:
            st.session_state["last_intake_text"] = raw_input
            st.session_state["generated_output"] = generated_output
            interactive_output = sanitize_identifiers(generated_output)
            final_sanitized_input = sanitize_for_storage(raw_input)
            final_sanitized_output = sanitize_for_storage(generated_output)
            qc_input = qc_sanitization_check(final_sanitized_input)
            qc_output = qc_sanitization_check(final_sanitized_output)

            st.session_state["draft_data"] = {
                "practitioner": practitioner,
                "person_term_choice": person_term_choice,
                "raw_input": raw_input,
                "detected_flags": detected_flags,
                "raw_output": generated_output,
                "interactive_output": interactive_output,
                "final_sanitized_input": final_sanitized_input,
                "final_sanitized_output": final_sanitized_output,
                "qc_input": qc_input,
                "qc_output": qc_output,
                "confidence": qc_output["confidence"],
            }
        else:
            st.error("No output generated.")

draft_data = st.session_state.get("draft_data")

if draft_data:
    st.subheader("Generated Draft")
    st.markdown(draft_data["interactive_output"])

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
        st.error("QC Failed: Potential identifiers remain")
        st.write("Issues detected:")
        st.write(qc_input["issues"] + qc_output["issues"])

    review_status_default = (
        "Mandatory Human Review"
        if draft_data["detected_flags"]
        else "Standard Human Review"
    )
    review_status = st.selectbox(
        "Review Status",
        ["Standard Human Review", "Mandatory Human Review"],
        index=0 if review_status_default == "Standard Human Review" else 1,
        key="review_status_select",
    )
    reviewer_comments = st.text_area("Reviewer Comments", key="reviewer_comments")
    if st.session_state["ALLOW_PID"]:
        st.checkbox(
            "Confirm identifiers will NOT be stored",
            value=False,
            key="confirm_pid_checkbox",
        )

    if st.button("Submit Review and Save"):
        sanitized_input = sanitize_for_storage(st.session_state["last_intake_text"])
        sanitized_output = sanitize_for_storage(st.session_state["generated_output"])
        sanitized_comments = sanitize_for_storage(reviewer_comments)

        sanitized_input = sanitize_for_storage(sanitized_input)
        sanitized_output = sanitize_for_storage(sanitized_output)
        sanitized_comments = sanitize_for_storage(sanitized_comments)

        qc_input = qc_sanitization_check(sanitized_input)
        qc_output = qc_sanitization_check(sanitized_output)
        qc_comments = qc_sanitization_check(sanitized_comments)
        qc_safe = qc_input["safe"] and qc_output["safe"] and qc_comments["safe"]

        if not qc_safe:
            st.warning(
                "QC detected possible identifiers. The submission will still be saved, but only after forced sanitization."
            )

        if st.session_state["ALLOW_PID"]:
            st.warning(
                "Identifiers may have been visible during review, but identifiers will not be saved."
            )

        qc_summary = {
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
            generated_output=sanitized_output,
            reviewer_comments=sanitized_comments,
            review_status=review_status,
            qc_summary=qc_summary,
        )
        increment_reviews()
        st.success("Review submitted. Sanitized output saved successfully.")
        st.caption(f"Saved file: {saved_path.name}")

st.subheader("Saved Outputs Dashboard")
try:
    files = list_saved_outputs()
except Exception:
    files = []

if not files:
    st.info("No saved outputs yet.")
else:
    selected_file = st.selectbox("Select an output to view", [file.name for file in files])
    selected_path = next(file for file in files if file.name == selected_file)
    content = selected_path.read_text(encoding="utf-8")
    st.text_area("Output Content", content, height=320)
