# Outputs Directory

## Always-Sanitized Save Behavior

The app saves review submissions after forcing identifier sanitization. Even when PID is visible during interaction or QC warnings are detected, the stored file contains only sanitized intake text, sanitized generated output, sanitized reviewer comments, detected flags, and QC metadata.

## Repository Visibility

Saved output artifacts are intended for local evaluation only and should not be committed or published with the repository. The repository keeps this folder scaffold for local runs, but generated markdown outputs should remain private and untracked.
