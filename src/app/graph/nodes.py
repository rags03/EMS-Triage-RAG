from .state import PainAssessmentState
from groq import Groq
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OPQRST_ORDER = [
    ("onset", "When did the pain start?"),
    ("provocation", "What makes the pain better or worse?"),
    ("quality", "Describe the quality of the pain (sharp, dull, burning, etc.)"),
    ("region", "Where is the pain located? Does it spread anywhere?"),
    ("severity", "How severe is the pain on a scale of 1-10?"),
    ("time", "How long has the pain been occurring? Has it changed over time?"),
]

def ask_question(state: PainAssessmentState) -> dict:
    for key, question in OPQRST_ORDER:
        if state.get(key) is None:
            return {"current_step": key, "current_question_text": question}
    return {"current_question_text": None, "complete": True}

def record_answer(state: PainAssessmentState) -> dict:
    step = state.get("current_step")
    user_input = state.get("user_input")
    return {step: user_input, "user_input": None}

def generate_summary(state: PainAssessmentState) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are an EMS triage assistant. 
Based on the OPQRST pain assessment below, give a clear recommendation on whether the patient should:
1. Call 911 immediately
2. Go to the ER today
3. See a doctor within 24-48 hours
4. Monitor at home and see a doctor if it worsens
             
Base your reasoning on established triage guidelines and provide evidence from sites such as:
- Mayo Clinic (mayoclinic.org)
- WebMD (webmd.com)
- American College of Emergency Physicians (acep.org)
- NIH MedlinePlus (medlineplus.gov)
             
Be concise and explain your reasoning. Also, make sure to remind the patient that you are NOT a doctor and that if they are in doubt, they should seek emergency care."""},
            {"role": "user", "content": f"""OPQRST Assessment:
- Onset: {state.get('onset')}
- Provocation: {state.get('provocation')}
- Quality: {state.get('quality')}
- Region: {state.get('region')}
- Severity: {state.get('severity')}
- Time: {state.get('time')}"""}
        ]
    )
    return {"summary": response.choices[0].message.content.strip()}