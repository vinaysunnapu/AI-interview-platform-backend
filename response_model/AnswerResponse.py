from typing import Optional
from pydantic import BaseModel

class AnswerResponse(BaseModel):
    InterviewEnded: bool
    nextQuestion: Optional[str] = None
    interviewerResponse: Optional[str] = None
    questionType: Optional[str] = None
    remainingSeconds: Optional[int] = None
    report: Optional[dict] = None
