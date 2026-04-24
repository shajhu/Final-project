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

## Identifier Protection (V1.2.1)

- All generated and stored outputs are sanitized
- Identifiers are replaced with bracket placeholders
- Raw identifiers are never persisted
- A configurable ALLOW_PID flag exists for future controlled use
- This feature is disabled by default
- This system remains non-HIPAA compliant and should not store real patient data

## Identifier Confidence System

Version 1.2.2 introduces a confidence flag system that evaluates whether identifier sanitization may be incomplete. This reinforces human review and reduces the risk of relying solely on automated masking.

This system is heuristic-based and not a substitute for formal de-identification.

## Usage Tracking

Version 1.2.5 introduces local usage tracking. This tracks only application interactions and does not store any identifying user or patient information.
