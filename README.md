

# Intake-to-Note Assistant

**Current Status:** Version 1.1

This Streamlit app converts intake responses into a structured review note, draft follow-up, and flagged concerns for human review. It supports multiple practitioner types and preserves human review boundaries.

## Version 1.1 Security Update
- Added environment-based API key handling
- Added privacy and safety reminders in the UI
- Added safety flag detection for higher-risk intake content
- Added security_notes.md documenting current privacy boundaries
- Added crypto_utils.py as an encryption-ready placeholder for future encrypted storage

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

## Important Privacy Note
This prototype should only be used with synthetic or non-identifying data. It is not HIPAA-ready and should not be used with real patient-identifying information.

## Local Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
setx OPENAI_API_KEY "your_api_key_here"
python -m streamlit run app.py
```

**Note:** `.env` and `.streamlit/secrets.toml` should not be committed to version control.

See `project_plan.md` for design details and `eval_set.md` for test cases.
