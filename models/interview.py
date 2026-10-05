from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InterviewStatusEnum(str,Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Answer(BaseModel):
    question: str
    answer: Optional[str]
    skip: bool = False
    assessment: Optional[str] = None


class InterviewSession(BaseModel):
    session_id: str
    status: InterviewStatusEnum = InterviewStatusEnum.IN_PROGRESS
    answers: list[Answer] = []
    introText: str = ""
    job_title: str = ""
    job_description: str = ""
    resume_text: str = ""
    current_question: str = ""
    follow_ups_on_topic: int = 0
    started_at: Optional[datetime] = None
    duration_seconds: int = 600
    report: Optional[dict] = None