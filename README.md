# Intake-to-Note Assistant

**Current Status:** Version 1.1

This Streamlit app converts intake responses into a structured review note, draft follow-up, and flagged concerns for human review. It supports multiple practitioner types and preserves human review boundaries.

## Version 1.1 Security Update
- Added environment-based API key handling
- Added privacy and safety reminders in the UI
- Added safety flag detection for higher-risk intake content
- Added security_notes.md documenting current privacy boundaries
- Added crypto_utils.py as an encryption-ready placeholder for future encrypted storage

## Version 1.2.1 Identifier Protection

- Added automatic identifier removal and masking
- Replaces names and IDs with placeholders (e.g., [NAME], [ID], [EMAIL])
- Prevents storage of identifiers in output files
- Introduced optional toggle for controlled identifier handling
- Strengthens privacy and testing safety

## Version 1.2.5 Dashboard and Tracking

- Added usage tracking (app runs and reviews submitted)
- Added dashboard to view saved outputs
- Introduced simple engagement metric to track adoption
- Designed for local testing, compatible with future cloud expansion

## Sanitization Confidence

Each saved output includes a confidence level:
- HIGH: low likelihood of remaining identifiers
- MEDIUM: possible identifiers remain
- LOW: likely identifiers remain

Manual review is required for all outputs.

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

## Dashboard and Tracking

- Outputs can be viewed within the app dashboard
- Usage metrics track:
  - total app runs
  - total reviews submitted
- Metrics are stored locally in usage.json and not committed to Git
