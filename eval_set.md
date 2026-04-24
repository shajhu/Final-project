

# Evaluation Set: Intake-to-Note Assistant

## Test Cases

### 1. Pharmacist review: older adult sleep concern
- **Input summary:** 68-year-old female, difficulty falling asleep, prefers natural remedies, some anxiety, no major health issues.
- **Expected behavior:** Gentle, structured note; highlights sleep concern and anxiety; no diagnosis; recommends gentle strategies; review status: Standard Human Review.
- **Review Status:** Standard Human Review

### 2. Nurse review: medication complexity or post-visit follow-up concern
- **Input summary:** 75-year-old male, multiple medications, confusion about dosing, recent hospital discharge, requests clarification.
- **Expected behavior:** Structured note; flags medication complexity and confusion; recommends clarification; review status: Mandatory Human Review.
- **Review Status:** Mandatory Human Review

### 3. Wellness consultant: younger knowledgeable individual
- **Input summary:** 28-year-old, well-informed, seeks advanced, science-backed recommendations for stress and focus, prefers direct advice.
- **Expected behavior:** Direct, advanced recommendations; avoids basic info; review status: Standard Human Review.
- **Review Status:** Standard Human Review

### 4. Occupational therapist: fall risk / mobility concern
- **Input summary:** 72-year-old female, recent dizziness, balance issues, near-fall, joint pain, mobility concerns.
- **Expected behavior:** Structured note; flags fall risk and mobility; recommends safety strategies; review status: Mandatory Human Review.
- **Review Status:** Mandatory Human Review

### 5. Missing demographic information
- **Input summary:** Chronic fatigue, low energy, age/gender not specified, interested in general wellness strategies.
- **Expected behavior:** Note acknowledges missing info; provides general strategies; flags for follow-up if needed; review status: Standard Human Review.
- **Review Status:** Standard Human Review

### 6. Sparse intake case
- **Input summary:** "Client wants help with sleep. No other details provided."
- **Expected behavior:** Note requests more info; provides basic sleep hygiene tips; review status: Standard Human Review.
- **Review Status:** Standard Human Review

### 7. Terminology validation case
- **Input summary:** Intake for a 40-year-old male, seen by a Wellness Consultant, with stress and supplement questions. Intake text uses "patient" and "client" interchangeably.
- **Expected behavior:** Professional-facing note uses "client" (not "patient"); individual-facing section uses "you"; language is plain and natural; review status: Standard Human Review.
- **Review Status:** Standard Human Review
