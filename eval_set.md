# Evaluation Set: Intake-to-Note Assistant

## Test Cases

1. **Older adult with sleep concerns**
   - Input: "Client is 68-year-old female, reports difficulty falling asleep due to evening anxiety. Prefers natural, gentle remedies over medications. Has tried chamomile tea with some success. No major health issues reported."
   - Expected: Structured note with gentle recommendations, safety check, no unnecessary escalation.

2. **Male client with stress**
   - Input: "Client is 45-year-old male, experiencing high work stress leading to irregular sleep and poor eating habits. Interested in stress management techniques and building better daily routines. Open to supplements but prefers evidence-based advice."
   - Expected: Note with stress management, routine advice, evidence-based supplement info.

3. **Missing demographics**
   - Input: "Client reports chronic fatigue and low energy levels. Age and gender not specified in form. Interested in general wellness strategies for better sleep and energy. No specific preferences mentioned."
   - Expected: Note acknowledges missing info, provides general strategies, flags for follow-up if needed.

4. **Younger, informed client**
   - Input: "Client is 28-year-old, well-informed about wellness products. Seeks practical, science-backed recommendations for managing stress and improving focus. Prefers direct, actionable advice without overly basic explanations."
   - Expected: Direct, advanced recommendations, avoids basic info.

5. **Fall risk case**
   - Input: "Client is 72-year-old female, reports recent dizziness and balance issues that have led to a near-fall. Also mentions joint pain affecting mobility. Seeking guidance on safe exercise and fall prevention strategies."
   - Expected: Note prioritizes safety, recommends fall prevention, flags for escalation if needed.

6. **Sparse intake**
   - Input: "Client wants help with sleep. No other details provided."
   - Expected: Note requests more info, provides basic sleep hygiene tips.
