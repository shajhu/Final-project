# API key is loaded from .env for local development
# Do not hardcode secrets

# Version 1.1: Safer model integration, privacy controls, encryption-ready structure
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_NAME = "gpt-4.1-mini"  # If model access fails, gpt-4o-mini may be used as a fallback

st.set_page_config(page_title="Intake-to-Note Assistant", layout="centered")
st.title("Intake-to-Note Assistant")
st.write("Converts intake responses into a structured review note, draft follow-up, and flagged concerns for human review.")

# Sidebar privacy and safety notes
with st.sidebar:
    st.header("Privacy and Safety Notes")
    st.markdown("""
    - Use synthetic or non-identifying data for testing
    - **Do not enter real patient-identifying information**
    - Outputs are drafts and require human review
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

def detect_flags(intake_text: str) -> list[str]:
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
    # Determine terminology for professional-facing note
    if practitioner in ["Pharmacist", "Nurse", "General Medical Reviewer"]:
        prof_term = "patient"
    elif practitioner == "Wellness Consultant":
        prof_term = "client"
    else:
        prof_term = "individual"

    # Section instructions
    prompt = f"""
You are an expert {practitioner} assistant. Your job is to convert intake responses into a structured review note, highlight key points, draft a summary for the individual, suggest next steps, and flag any concerns for human review.

Always follow these rules:
- Draft only. Human review required before use.
- Do NOT diagnose or make final treatment decisions.
- Do NOT make medication, supplement, or interaction claims unless clearly supported by the intake text.
- Escalate higher-risk concerns, including fall risk, severe symptoms, medication complexity, incomplete information, or unclear safety concerns.
- Adapt note framing and terminology to the selected practitioner type. Use "{prof_term}" for professional-facing sections. For individual-facing sections, use second-person language ("you").
- Use professional, natural, and supportive language.

Generate exactly these sections:
1. Structured Review Note (professional-facing, concise, organized, uses "{prof_term}", no diagnosis or final treatment decisions)
2. Key Intake Highlights (bullet-style summary of important intake details)
3. Individual-Facing Summary (plain language, written directly to the individual using "you", supportive, no jargon)
4. Suggested Next Steps (general, safe, draft recommendations only, no prescriptions, no autonomous treatment decisions)
5. Flagged Concerns (list detected risks or safety concerns clearly)
6. Review Status (must be one of: Standard Human Review, Mandatory Human Review)

Practitioner type: {practitioner}
Preferred tone: {tone}
{prof_term.capitalize()} age: {client_age or 'Not provided'}
Goals or main concern: {client_goals or 'Not provided'}
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
    return OpenAI(api_key=api_key)

def call_llm(prompt):
    client = get_openai_client()
    if not client:
        return None, "Missing API key."
    try:
        # Use the OpenAI Responses API pattern for safer integration
        response = client.responses.create(
            model=MODEL_NAME,
            prompt=prompt,
            max_tokens=1200,
            temperature=0.3
        )
        return response.output_text, None
    except Exception as e:
        # If model access fails, gpt-4o-mini may be used as a fallback (see MODEL_NAME comment)
        return None, f"OpenAI API error: {e}"

if st.button("Generate Draft"):
    if not intake_text.strip():
        st.warning("Please enter intake form responses.")
    else:
        flags = detect_flags(intake_text)
        if flags:
            st.error("Potential safety flags detected. Mandatory human review recommended.")
        else:
            st.info("No automatic safety flags detected. Standard human review still required.")
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
