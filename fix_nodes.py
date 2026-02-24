lines = [
    'print("NODES.PY LOADED")\n',
    'from .state import PainAssessmentState\n',
    '\n',
    'OPQRST_ORDER = [\n',
    '    ("onset", "When did the pain start?"),\n',
    '    ("provocation", "What makes the pain better or worse?"),\n',
    '    ("quality", "Describe the quality of the pain."),\n',
    '    ("region", "Where is the pain located?"),\n',
    '    ("severity", "How severe is the pain on a scale of 1-10?"),\n',
    '    ("time", "How long has the pain been occurring? Has it changed over time?"),\n',
    ']\n',
    '\n',
    'def ask_question(state: PainAssessmentState) -> dict:\n',
    '    for key, question in OPQRST_ORDER:\n',
    '        if state.get(key) is None:\n',
    '            return {\n',
    '                "current_step": key,\n',
    '                "current_question_text": question,\n',
    '                "complete": False\n',
    '            }\n',
    '    return {\n',
    '        "current_question_text": "Thank you for providing all the information about your pain.",\n',
    '        "complete": True\n',
    '    }\n',
    '\n',
    'def record_answer(state: PainAssessmentState) -> dict:\n',
    '    step = state.get("current_step")\n',
    '    user_input = state.get("user_input")\n',
    '    return {\n',
    '        step: user_input,\n',
    '        "user_input": None\n',
    '    }\n',
]

with open('src/app/graph/nodes.py', 'w') as f:
    f.writelines(lines)

print('Done - nodes.py rewritten')