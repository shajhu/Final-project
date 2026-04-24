import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Intake-to-Note Assistant", layout="centered")
st.title("Intake-to-Note Assistant")
st.write("Converts intake responses into a structured review note, draft follow-up, and flagged concerns for human review.")

# Sidebar usage notes
with st.sidebar:
    st.header("Usage Notes")
    st.markdown("""
    - This prototype uses synthetic or user-provided test data only
    - **Do not enter real patient-identifying information**
    - Outputs are drafts and require review
    - High-risk cases should not be handled automatically
    - This app is not intended for diagnosis or autonomous treatment decisions
    """)

practitioner_types = [
    "Pharmacist",
    "Nurse",
    "Wellness Consultant",
    "Occupational Therapist",
    "General Medical Reviewer"
]

practitioner = st.selectbox("Practitioner Type", practitioner_types)

intake_text = st.text_area("Paste Intake Form Responses", height=200)

col1, col2 = st.columns(2)
with col1:
    client_age = st.text_input("Client Age (optional)")
    client_goals = st.text_input("Client Goals (optional)")
with col2:
    current_meds = st.text_input("Current Medications/Supplements (optional)")
    relevant_concerns = st.text_input("Relevant Concerns/Safety Flags (optional)")

tone = st.selectbox("Preferred Tone (optional)", ["Gentle", "Direct", "Professional"], index=2)

def detect_flags(intake_text: str) -> list:
    keywords = [
        "fall", "dizziness", "fainting", "medication", "blood thinner", "pregnant", "chest pain", "severe",
        "confusion", "emergency", "interaction", "allergy", "shortness of breath", "suicidal", "overdose"
    ]
    flags = []
    text = intake_text.lower() if intake_text else ""
    for word in keywords:
        if word in text:
            flags.append(word)
    return list(set(flags))

def build_system_prompt(practitioner, tone, client_age, client_goals, current_meds, relevant_concerns, flags, intake_text):
    prompt = f"""
You are an expert {practitioner} assistant. Your job is to convert intake responses into a structured review note, highlight key points, draft a client-facing follow-up, and flag any concerns for human review. 

Always follow these rules:
- Do NOT diagnose or make definitive treatment instructions.
- Do NOT make medication, supplement, or interaction claims unless clearly supported by the intake text.
- Flag possible fall risk, severe symptoms, medication complexity, unclear safety concerns, allergies, pregnancy, confusion, emergency symptoms, or incomplete information.
- State when a trained professional should review before any recommendation is shared.
- Treat all outputs as drafts only.
- Use clear language that supports, but does not replace, professional judgment.

Generate exactly these sections:
1. Structured Review Note
2. Key Intake Highlights
3. Draft Client-Facing Follow-Up
4. Flagged Concerns
5. Review Status (must be one of: Standard Human Review, Mandatory Human Review)

Practitioner type: {practitioner}
Preferred tone: {tone}
Client age: {client_age or 'Not provided'}
Client goals: {client_goals or 'Not provided'}
Current medications/supplements: {current_meds or 'Not provided'}
Relevant concerns/safety flags: {relevant_concerns or 'None'}
Detected safety flags: {', '.join(flags) if flags else 'None'}

Intake responses:
"""
    prompt += intake_text.strip() if intake_text else ""
    prompt += """

If any detected safety flags are present, set Review Status to Mandatory Human Review and clearly highlight the concern(s).
"""
    return prompt

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY environment variable not set. Please set it in your environment or .env file.")
        return None
    return OpenAI()

def call_llm(prompt):
    client = get_openai_client()
    if not client:
        return None, "Missing API key."
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1200,
            temperature=0.3
        )
        return response.choices[0].message.content, None
    except Exception as e:
        # Fallback to gpt-4o-mini if access issue
        if "model" in str(e) and "gpt-4.1-mini" in str(e):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=1200,
                    temperature=0.3
                )
                return response.choices[0].message.content, None
            except Exception as e2:
                return None, f"OpenAI API error: {e2}"
        return None, f"OpenAI API error: {e}"

if st.button("Generate Draft"):
    if not intake_text.strip():
        st.warning("Please enter intake form responses.")
    else:
        flags = detect_flags(intake_text)
        if flags:
            st.error("Potential safety flags detected. Mandatory human review recommended.")
        st.info("Draft only. Requires human review before use.")
        if flags:
            st.write(f"**Detected Flags:** {', '.join(flags)}")
        prompt = build_system_prompt(
            practitioner, tone, client_age, client_goals, current_meds, relevant_concerns, flags, intake_text
        )
        with st.spinner("Generating draft..."):
            output, err = call_llm(prompt)
        if err:
            st.error(err)
        elif output:
            st.markdown(output)
        else:
            st.error("No output generated.")
