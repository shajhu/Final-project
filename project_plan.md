# Project Plan: Intake-to-Note Assistant

## 1. User & Workflow
- **User:** Wellness consultant or intake reviewer
- **Workflow:** Paste intake form text → Generate structured note → Review/edit → Copy to EHR or consult note

## 2. Design & Baseline
- **Goal:** Transform unstructured intake text into a structured, actionable note
- **Baseline:** Manual review and note writing
- **GenAI Approach:** Prompt engineering, context management, safety controls

## 3. Prompt & Model
- **Prompt:** System prompt for tone, structure, safety, and escalation
- **Model:** OpenAI GPT-4.1 (or similar)

## 4. Evaluation
- **Eval set:** See `eval_set.md` for 5 diverse test cases
- **Metrics:** Structure, accuracy, safety, personalization, triage/escalation
- **Comparison:** Baseline vs. GenAI output

## 5. Risks & Controls
- **Risks:** Hallucination, missed safety issues, over/under-triage
- **Controls:** Prompt constraints, output review, escalation triggers

## 6. Example Inputs and Failure Cases

### Example Inputs

1. **Older adult with sleep concerns and preference for gentle solutions**  
   Intake text: "Client is 68-year-old female, reports difficulty falling asleep due to evening anxiety. Prefers natural, gentle remedies over medications. Has tried chamomile tea with some success. No major health issues reported."

2. **Male client with stress and routine challenges**  
   Intake text: "Client is 45-year-old male, experiencing high work stress leading to irregular sleep and poor eating habits. Interested in stress management techniques and building better daily routines. Open to supplements but prefers evidence-based advice."

3. **Intake with missing demographic information**  
   Intake text: "Client reports chronic fatigue and low energy levels. Age and gender not specified in form. Interested in general wellness strategies for better sleep and energy. No specific preferences mentioned."

4. **Younger client with higher familiarity and expectations**  
   Intake text: "Client is 28-year-old, well-informed about wellness products. Seeks practical, science-backed recommendations for managing stress and improving focus. Prefers direct, actionable advice without overly basic explanations."

5. **Case including fall risk or functional concerns**  
   Intake text: "Client is 72-year-old female, reports recent dizziness and balance issues that have led to a near-fall. Also mentions joint pain affecting mobility. Seeking guidance on safe exercise and fall prevention strategies."

6. **Sparse or incomplete intake**  
   Intake text: "Client wants help with sleep. No other details provided."

---

### Failure Cases

1. Cases with complex medical or medication-related risks that exceed the scope of a wellness consult (e.g., active medication interactions or undiagnosed conditions requiring clinical review)
2. Sparse or contradictory inputs that may lead to generic or weak outputs (e.g., minimal details making it hard to personalize or identify risks)
3. Inputs with potential safety signals that are not clearly flagged (e.g., subtle mentions of mental health concerns or substance use that need escalation)

---

## 7. Risks and Governance

The system may fail by:
- producing overly confident language,
- missing subtle risk indicators,
- generating outputs that appear correct but are incomplete.

The system should not be trusted for:
- diagnosis
- treatment decisions
- high-risk or unclear cases without review

Governance controls include:
- mandatory human review for flagged cases
- avoidance of diagnostic language
- clear positioning as a draft-generation tool
- use of synthetic data only for development

---

## 8. Plan for the Week 6 Check-in

By Week 6, the following will be completed:

- a working Streamlit app with intake input and generated outputs
- a first version of the structured prompt
- initial evaluation cases
- baseline vs structured output comparison on at least one case

This will allow demonstration of:
- core functionality
- early evaluation
- initial improvements over baseline

---

## 9. Pair Request

Not applicable.
