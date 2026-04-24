# Security and Privacy Notes

## Current V1.1 Controls
- API keys are stored outside the codebase using environment variables or .env files
- .env must not be committed to GitHub
- The app displays privacy reminders
- The app is intended for synthetic or non-identifying test data only
- Outputs are draft-only and require human review

## Encryption Readiness
This prototype does not store real patient data. If persistent storage is added later, notes and intake data should be encrypted at rest before being saved. Future versions may add a local encryption utility using a managed encryption key or deployment platform secret store.

## Deployment Boundary
This prototype is not HIPAA-ready and should not be used with real patient-identifying information until appropriate privacy, access control, logging, consent, and compliance safeguards are implemented.
