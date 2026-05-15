# DraftSafe™

AI-Assisted Practitioner Documentation & Review

**Current Status:** Version 1.5.0

DraftSafe™ is a Streamlit prototype that supports practitioner documentation workflows for fragmented intake material. It combines AI-assisted draft generation, lightweight deterministic validation, and structured human review without replacing practitioner judgment.

## Full Reset / Restart

Use this when the local app, tunnel, or dashboard session gets into a bad state.

```powershell
taskkill /F /IM python.exe
taskkill /F /IM ngrok.exe
Set-Location "C:\Users\shami\OneDrive\Documents\John Hopkins\Generative AI\Repository\Final Project"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py --server.port 8501
```

After Streamlit starts, open `http://localhost:8501`.

## Setup & Usage

### First-time local setup

```powershell
Set-Location "C:\Users\shami\OneDrive\Documents\John Hopkins\Generative AI\Repository\Final Project"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
setx OPENAI_API_KEY "your_api_key_here"
```

### Run locally

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py --server.port 8501
```

### Optional ngrok sharing

Run this in a second terminal after the app is already running:

```powershell
ngrok http 8501
```

Keep both the Streamlit terminal and the ngrok terminal open during remote testing.

### Quick usage flow

1. Select a practitioner type.
2. Paste synthetic or non-identifying intake content.
3. Generate the draft.
4. Review practitioner-specific triggers and deterministic audit results.
5. Complete human review and save the sanitized output.

## Streamlit Community Cloud Deployment

DraftSafe™ is prepared for Streamlit Community Cloud without changing the local workflow.

### Deployment checklist

- Entrypoint: `app.py`
- Python version: use `runtime.txt`
- Dependencies: install from `requirements.txt`
- Required secret: `OPENAI_API_KEY`
- Optional admin secret for restricted output review access: `DRAFTSAFE_ADMIN_KEY`
- Local output behavior remains unchanged
- Deployed output handling uses temporary writable storage and may reset between sessions or redeploys

### Recommended Streamlit secrets

```toml
OPENAI_API_KEY = "your_api_key_here"
# Optional:
# DRAFTSAFE_ADMIN_KEY = "your_admin_key_here"
```

### Deployment notes

- Do not commit real secrets, `.env`, or Streamlit secrets files.
- The deployment keeps the app lightweight and session-oriented.
- The auxiliary skill remains separate from the deployed app.
- Cloud-saved outputs are intended for demo and evaluation use and should be treated as temporary.

## Context, User, and Problem

DraftSafe™ is aimed at practitioners reviewing fragmented intake documentation, especially:

- occupational therapists
- pharmacists
- practitioners who need a fast first-pass draft from incomplete intake material

The workflow problem is narrow and practical:

- intake details often arrive incomplete or scattered
- documentation burden slows review work
- missing details are easy to overlook in repetitive workflows
- review consistency suffers when the first draft is unstructured

This project focuses on documentation support rather than autonomous clinical decision-making.

## Solution & Workflow Design

DraftSafe™ combines:

- AI-assisted draft generation
- lightweight deterministic validation
- practitioner-specific workflow support
- structured documentation review assistance

The core workflow is:

`intake -> AI draft -> audit/validation -> human review`

DraftSafe™ is designed to support documentation workflows rather than replace practitioner judgment.

Design choices kept intentionally lightweight:

- Streamlit single-app interface
- model adapter for provider abstraction
- deterministic audit layer for transparent review support
- session-based visibility for generated outputs
- local file save flow for simple evaluation and demonstration

## Auxiliary Skill Module

The auxiliary skill remains modular and separate from the main app.

Companion skill path:

```text
.agents/skills/clinical-gap-audit/
```

Its role is to preserve a standalone skill artifact for modular evaluation of the clinical-gap audit logic without merging that implementation into `app.py`.

This separation keeps:

- the Streamlit app focused on the user workflow
- the auxiliary skill independently reviewable
- the submission aligned with modularity expectations

## Evaluation & Baseline Comparison

Evaluation materials are organized around the project workflow rather than benchmark-style model claims.

Primary comparison framing:

- baseline: a plain draft-generation workflow with no practitioner-specific cue handling and no deterministic audit support
- DraftSafe™: practitioner-specific prompting plus deterministic audit and explicit human review framing

Evaluation emphasis:

- whether fragmented intake information is organized more clearly
- whether missing details are surfaced more consistently
- whether review status is made more explicit
- whether the output remains usable as a draft rather than overstating certainty

Reference files:

- `eval_set.md`
- `project_plan.md`

## Results & Limitations

Observed strengths of the workflow:

- improves first-draft structure for fragmented intake content
- makes missing documentation details more visible
- reinforces review status and human-review expectations
- provides practitioner-specific framing without changing the underlying intake facts

Current limitations:

- output quality still depends on intake quality
- deterministic audit logic is narrow and heuristic by design
- pharmacist and OT support are stronger than unsupported practitioner types
- saved cloud outputs are temporary in deployed environments
- the system is not HIPAA-ready and is not intended for real identifying data

## Human Review & Safety Boundaries

Human review remains mandatory for every generated output.

DraftSafe™ does not:

- diagnose
- make autonomous treatment decisions
- replace licensed practitioner judgment
- guarantee complete identifier removal in every case

Safety boundaries built into the workflow:

- identifier sanitization before save
- deterministic review cues and audit status support
- explicit review completion workflow
- mandatory escalation framing for higher-risk or incomplete cases
- admin-only saved-output access disabled unless a private key is explicitly configured

## Artifact Snapshot

Key repository artifacts:

- `app.py`: Streamlit app and practitioner workflow
- `audit_layer.py`: deterministic audit logic
- `model_adapter.py`: model abstraction layer
- `outputs/README.md`: local-output folder guidance without committed saved artifacts
- `assets/`: branding and presentation assets
- `eval_set.md`: evaluation cases
- `project_plan.md`: project design notes
- `security_notes.md`: privacy and security notes
- `runtime.txt`: Streamlit Cloud Python runtime pin

## Demo Workflow

Suggested grader/demo path:

1. Launch the app locally or through Streamlit Cloud.
2. Choose `Pharmacist` or `Occupational Therapist`.
3. Paste a short synthetic fragmented intake.
4. Generate the draft.
5. Review the deterministic audit summary and review status.
6. Submit review and save the sanitized output.
7. Inspect the local saved markdown artifact only when running in a private local environment.

This path allows a grader to clone, install, run, and evaluate the workflow within minutes.

## Output Handling

Local development behavior:

- outputs save to `outputs/`
- saved files contain sanitized intake text and sanitized generated output only
- reviewer comments are sanitized before save
- saved artifacts are intended to remain local and private

Deployed behavior:

- the same save workflow is preserved
- deployed environments use temporary writable storage
- cloud-saved artifacts are not treated as durable or public storage

Repository behavior:

- generated markdown outputs are not included in the public repository
- the app shows generated content only within the active session for non-admin users

This keeps output handling lightweight, deterministic, and demo-safe without introducing database infrastructure.

## Troubleshooting

### App will not start

- confirm the virtual environment is activated
- confirm dependencies were installed with `pip install -r requirements.txt`
- confirm `OPENAI_API_KEY` is set locally or in Streamlit secrets

### Port 8501 is busy

```powershell
taskkill /F /IM python.exe
taskkill /F /IM ngrok.exe
```

Then rerun the app.

### Streamlit Cloud generates a secret error

- add `OPENAI_API_KEY` to the Streamlit Cloud secrets panel
- redeploy or rerun the app after saving the secret

### Admin-only output review is unavailable

- this is expected unless `DRAFTSAFE_ADMIN_KEY` is configured privately
- without that key, saved-output review remains disabled in the interface

### Outputs do not persist in deployment

- this is expected for ephemeral cloud runs
- use local runs when persistent saved artifacts are needed for evaluation

### Testing reminder

- use synthetic or non-identifying data only
- do not use real patient-identifying information

## Version History

## V1.5.0 — Submission Lock Release

- finalized README structure for submission and grading speed
- aligned repository documentation to workflow-focused rubric language
- clarified setup, deployment, evaluation, modularity, and privacy sections
- removed committed saved-output artifacts from the repository
- disabled admin-only output access unless a private admin key is configured
- preserved top-of-file reset and setup guidance
- preserved version history at the bottom of the README

## V1.4.9 — Deployment Readiness Release

- added Streamlit Community Cloud deployment preparation
- added deployment-safe secret lookup for local env or Streamlit secrets
- preserved local output folder behavior for development
- added temporary writable storage fallback for deployed environments
- kept audit workflows, UI behavior, and practitioner logic unchanged
- preserved auxiliary skill modularity and local/ngrok workflows

## V1.4.7 — Demo Stabilization & Visual Audit Polish

- added lightweight audit dashboard metrics
- added documentation completeness progress bar
- added review status indicators
- added detected review area summaries
- preserved session-only output visibility
- refined presentation and demo readiness

## V1.4.5 — Monochromatic Branding Integration

- integrated finalized monochromatic DraftSafe™ logo
- added branded responsive application header
- improved visual identity and title alignment

## V1.4.4 — Branding & Ownership Protection Update

- standardized DraftSafe™ branding
- added ownership and repository protection language

## V1.4.3 and Earlier

- added attachment support, dashboard fallbacks, practitioner-specific prompting, sanitization safeguards, and review workflow refinements across earlier releases