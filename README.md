
# Intake-to-Note Assistant

**Current Status:** Version 1 prototype

This Streamlit app converts intake responses into a structured review note, draft follow-up, and flagged concerns for human review. It supports multiple practitioner types and preserves human review boundaries.

## Supported Practitioner Types
- Pharmacist
- Nurse
- Wellness Consultant
- Occupational Therapist
- General Medical Reviewer

## Human Review Boundary
- All outputs are drafts only and require human review before use.
- High-risk cases (e.g., flagged safety concerns) are always escalated for mandatory review.
- The app does not diagnose or make autonomous treatment decisions.

## No Real Patient Data
- This prototype uses only synthetic or user-provided test data.
- **Do not enter real patient-identifying information.**

## Setup & Run Instructions

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
setx OPENAI_API_KEY "your_api_key_here"
streamlit run app.py
```

**Note:** `.env` should not be committed to version control.

See `project_plan.md` for design details and `eval_set.md` for test cases.
