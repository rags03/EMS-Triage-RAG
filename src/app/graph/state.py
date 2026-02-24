from typing import Optional
from typing_extensions import TypedDict

class PainAssessmentState(TypedDict, total=False):
    onset: Optional[str]
    provocation: Optional[str]
    quality: Optional[str]
    region: Optional[str]
    severity: Optional[str]
    time: Optional[str]
    current_step: Optional[str]
    current_question_text: Optional[str]
    user_input: Optional[str]
    complete: bool
    summary: Optional[str]