import uuid
import math
from datetime import datetime, timezone
from models.interview import Answer, InterviewSession, InterviewStatusEnum
from store.session_store import SESSION_STORE

def create_session(job_title: str, job_description: str, resume_text: str) -> InterviewSession:
    session_id = str(uuid.uuid4())

    interview_session = InterviewSession(
        session_id=session_id,
        job_title=job_title,
        job_description=job_description,
        resume_text=resume_text,
    )

    SESSION_STORE[session_id] = interview_session

    return interview_session

def get_session(session_id: str) -> InterviewSession:
    session = SESSION_STORE.get(session_id)

    if not session:
        return None 
    return session

def start_session(session: InterviewSession) -> None:
    if session.started_at is None:
        session.started_at = datetime.now(timezone.utc)

def remaining_seconds(session: InterviewSession) -> int:
    if session.started_at is None:
        return session.duration_seconds

    elapsed = (datetime.now(timezone.utc) - session.started_at).total_seconds()
    return max(0, math.ceil(session.duration_seconds - elapsed))

def save_answer(answer: str | None, skip: bool, session: InterviewSession) -> None:
    session.answers.append(
        Answer(
            question=session.current_question,
            answer=None if skip else answer,
            skip=skip,
        )
    )

def complete_session(session: InterviewSession) -> None:
    session.status = InterviewStatusEnum.COMPLETED