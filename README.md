# Intake-to-Note Assistant

**Current Status:** Version 1.4.3

This Streamlit app assists practitioner-specific documentation by identifying relevant concepts, highlighting gaps, and drafting reviewable assessment and follow-up language for human review. It supports multiple practitioner types and preserves human review boundaries.

## Model Architecture

The system uses a model adapter layer to allow future integration with multiple AI providers (e.g., OpenAI, Claude).

Current state:
- OpenAI only (active)
- Other adapters are placeholders

## Version 1.4.2 Targeted Evaluation Alignment

- Improved trigger detection with lightweight semantic cue grouping
- Tightened pharmacist prompt language to avoid overclaiming interaction risk
- Updated OT auto terminology to default to patient
- Added optional assignment-aligned output section format
- Clarified system-added content labeling and cue count display

## Version 1.4 Practitioner-Specific Assistant Upgrade

- Transitioned from summary generation to practitioner-specific documentation assistance
- Added trigger detection by practitioner type
- Added documentation gap detection
- Added OT-focused reasoning around findings, deficits, functional impact, justification, and intervention
- Added nurse medication-safety documentation cues
- Added pharmacist supplement/medication review cues
- Added wellness consultant advisory boundaries
- Maintains human review, sanitization, and safe storage controls

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

## Version 1.3 Controlled PID and QC

- Added admin-gated PID visibility during interaction
- Enforced sanitization before model input when protection is on and before every save in all cases
- Added a QC loop that checks both sanitized input and sanitized output before saving
- Surfaces QC findings to reviewers before save
- Keeps saved outputs sanitized even when identifiers are visible during interaction

## Version 1.3.1 Always-Sanitized Save

- Review submissions now always save after forced sanitization
- PID may be visible during controlled review but is not persisted
- QC warnings are captured as metadata instead of blocking storage
- Reviewer comments are also sanitized before saving
- Improves evaluation data capture while preserving privacy safeguards

## Version 1.3.2 Session-Isolated Visibility

- Generated output is visible only within the current session
- Historical saved outputs are hidden from general users
- Admin mode can review all saved outputs through a protected dashboard
- Saved outputs still persist locally for audit and review
- Session reset support clears current-session data without exposing prior outputs

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

## Restart / Run Instructions

Use these steps when restarting the app for local testing or sharing through ngrok.

### 1. Open the project folder

Open the repository folder in VS Code:

```powershell
cd "C:\Users\shami\OneDrive\Documents\John Hopkins\Generative AI\Repository\Final Project"
```

### 2. Activate the virtual environment

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of the terminal line.

### 3. Start the Streamlit app

```powershell
python -m streamlit run app.py --server.port 8501
```

If port `8501` is already in use, either close old Python processes or use a different port:

```powershell
taskkill /F /IM python.exe
python -m streamlit run app.py --server.port 8501
```

### 4. Open locally

After the app starts, open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

### 5. Share remotely with ngrok

In a second terminal, run:

```powershell
ngrok http 8501
```

Copy the HTTPS forwarding link that ngrok provides, for example:

```text
https://example-name.ngrok-free.dev
```

Send that link to the tester.

### 6. Keep the app running

For remote testing, keep both terminals open:

- Terminal 1: Streamlit app
- Terminal 2: ngrok tunnel

The shared link will stop working if either terminal is closed, the laptop sleeps, or the internet connection drops.

### 7. Clean shutdown

When testing is complete, close everything with:

```powershell
taskkill /F /IM python.exe
taskkill /F /IM ngrok.exe
```

### Testing Notes

- Use synthetic or non-identifying data only.
- Do not enter real patient-identifying information.
- Outputs are sanitized before saving.
- Saved test outputs are stored locally in the `outputs/` folder.
- The app is a prototype and all outputs require human review.

**Note:** `.env` and `.streamlit/secrets.toml` should not be committed to version control.

See `project_plan.md` for design details and `eval_set.md` for test cases.

## Dashboard and Tracking

- Outputs can be viewed within the app dashboard
- Usage metrics track:
  - total app runs
  - total reviews submitted
- Metrics are stored locally in usage.json and not committed to Git

## PID Toggle (Session-Based)

- Identifier handling is controlled via a sidebar toggle
- Default behavior masks all identifiers
- Toggle uses Streamlit session state for persistence
- No global variables are used
- Designed for safe testing and future extensibility

## Storage Safety

- Raw identifiers are never written to disk
- Saved files contain sanitized intake text and sanitized generated output only
- Reviewer comments are sanitized before save
- QC validation runs before save and is stored as metadata
- Manual review is required for every saved output
