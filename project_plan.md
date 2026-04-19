
# 1. Project Title

Intake-to-Note Assistant for Pharmacist Review

---

# 2. Target User, Workflow, and Business Value

- **User:** Pharmacist or wellness consultant reviewing intake data
- **Recurring Task:** Transforming unstructured intake form text into a structured provider note, draft client-facing follow-up, and flagged concerns
- **Workflow:**
  - **Start:** Upon receipt of a new intake form
  - **Steps:** Paste intake form text → Generate structured provider note + draft client follow-up + flagged concerns → Review/edit outputs → Copy to consult documentation
  - **End:** When a structured note, draft follow-up, and flagged concerns are ready for documentation
- **Business Value:**
  - Manual review is time-consuming and error-prone. Automating first-pass documentation increases efficiency, standardizes notes, and helps ensure safety concerns are not missed, supporting better patient outcomes and workflow scalability.

---

# 3. Problem Statement and GenAI Fit

Manual review of unstructured intake data is slow, inconsistent, and risks missing important details. Pharmacists and wellness consultants need to efficiently convert intake text into structured notes and identify cases needing escalation.

This is a strong fit for GenAI because:
- Intake data is language-heavy, variable, and requires summarization and contextual understanding.
- Generative AI can produce structured, personalized outputs and adapt to varied inputs.
- A simpler non-GenAI tool (e.g., rules-based or template system) would not handle the variability, nuance, or natural language generation required for this workflow.

---

# 4. Planned System Design and Baseline

**Planned App:**
- Streamlit app with:
  - Intake input field
  - Generate button
  - Output panel displaying: structured provider note, draft client follow-up, flagged concerns, and review status

**Workflow/Architecture:**
- User pastes intake text
- LLM (via structured prompt) generates outputs
- Outputs are reviewed/edited by the user
- Finalized note is copied to documentation
- Boundary: Draft-generation and review support only; no diagnosis or autonomous treatment decision-making

**Baseline:**
- Manual review and note writing, or a simple unconstrained prompt without structured output or escalation logic

**Course Concepts:**
- **Structured Prompting / LLM Call Design:** Prompts constrain LLM output into labeled sections for consistency and reliability
- **Evaluation Design:** Rubric and test set will compare baseline (manual/unconstrained) vs. improved system outputs
- **Governance and Human Review Controls:** Escalation rules for high-risk scenarios; human review required for flagged cases

---

# 5. Evaluation Plan

**Success Criteria:**
- Outputs are structured, readable, and professional
- Intake details are accurately reflected
- Tone is appropriate for provider and client
- Unsafe or overconfident recommendations are avoided
- High-risk cases are correctly flagged for human review

**What Will Be Measured:**
- Structure consistency (all required sections present)
- Personalization (output reflects unique intake details)
- Tone quality (professional, appropriate for audience)
- Safety/escalation accuracy (correctly flags risk)

**Test Set:**
- 5–6 intake cases (normal, edge, high-risk scenarios)

**Comparison:**
- Outputs will be compared to baseline using a rubric

---

# 6. Example Inputs and Failure Cases

## Example Inputs

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

## Failure Cases

1. Cases with complex medical or medication-related risks that exceed the scope of a wellness consult (e.g., active medication interactions or undiagnosed conditions requiring clinical review)
2. Sparse or contradictory inputs that may lead to generic or weak outputs (e.g., minimal details making it hard to personalize or identify risks)
3. Inputs with potential safety signals that are not clearly flagged (e.g., subtle mentions of mental health concerns or substance use that need escalation)

---

# 7. Risks and Governance

**Where the System Could Fail:**
- Producing overly confident language
- Missing subtle risk indicators
- Generating outputs that appear correct but are incomplete

**Where It Should Not Be Trusted:**
- Diagnosis
- Treatment decisions
- High-risk or unclear cases without review

**Controls and Review Boundaries:**
- Mandatory human review for flagged cases
- Avoidance of diagnostic language
- Clear positioning as a draft-generation tool
- Use of synthetic data only for development

---

# 8. Plan for the Week 6 Check-in

By Week 6, the following will be completed:
- A working Streamlit app with intake input and generated outputs
- A first version of the structured prompt
- Initial evaluation cases
- Baseline vs. structured output comparison on at least one case

This will allow demonstration of:
- Core functionality
- Early evaluation
- Initial improvements over baseline

---

# 9. Pair Request

Not applicable.
