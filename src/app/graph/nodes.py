from .state import PainAssessmentState
from ..rag.retriever import retrieve
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
    query = f"{state.get('quality')} pain in {state.get('region')} severity {state.get('severity')} onset {state.get('onset')}"
    context = retrieve(query)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are an EMS triage assistant.
Based STRICTLY on the retrieved medical context below, give a clear recommendation on whether the patient should:
1. Call 911 immediately
2. Go to the ER today
3. See a doctor within 24-48 hours
4. Monitor at home and see a doctor if it worsens

Retrieved medical context:
{context}

IMPORTANT RULES:
- You MUST base your recommendation strictly on the retrieved context above
- Quote or reference specific information from the context in your reasoning
- Do not use knowledge outside of the provided context
- If the context does not contain enough information, say so explicitly

Always remind the patient you are NOT a doctor and if in doubt, seek emergency care."""},
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