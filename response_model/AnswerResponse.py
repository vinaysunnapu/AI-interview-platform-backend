from typing import Optional
from pydantic import BaseModel

class AnswerResponse(BaseModel):
    InterviewEnded: bool
    nextQuestion: Optional[str] = None
