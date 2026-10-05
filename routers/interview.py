from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models.interview import InterviewStatusEnum
from request_model.AnswerRequest import AnswerRequest
from response_model.AnswerResponse import AnswerResponse
from services.ai_service import generate_next_turn, generate_questions_intro, generate_report
from services.interview_service import (
    complete_session,
    create_session,
    get_session,
    remaining_seconds,
    save_answer,
    start_session,
)
from util.file_util import extract_text, validate_file

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)

@router.post("/generate_question")
async def generate_questions(
    job_title: str = Form(...),
    job_description = Form(...),
    resume: UploadFile  = File(...)
):
    # validate resume file
    await validate_file(resume)
    # extract text from resume
    resume_text = await extract_text(resume)
    # Generate questions and intro text using title, description and resume
    resp = await generate_questions_intro(job_title=job_title, job_description=job_description, resume_text=resume_text)
    first_question = resp.get("first_question")
    if not isinstance(first_question, str) or not first_question.strip():
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI could not generate the opening interview question")

    session = create_session(job_title, job_description, resume_text)
    session.current_question = first_question.strip()
    session.introText = resp.get("introText")

    return {
    "session_id": str(session.session_id)
}

@router.get("/start/{session_id}")
async def start_interview(session_id: str):
    #check and validate session id
    session = get_session(session_id)

    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    start_session(session)
    time_remaining = remaining_seconds(session)
    if time_remaining == 0:
        complete_session(session)
        session.report = await generate_report(session.answers, session.job_title)
        return {"InterviewEnded": True, "remainingSeconds": 0, "report": session.report}

    return {
        "introText": session.introText,
        "firstQuestion": session.current_question,
        "durationSeconds": session.duration_seconds,
        "remainingSeconds": time_remaining,
    }

@router.post("/submit", response_model= AnswerResponse)
async def submit_answer(answerReq: AnswerRequest):
    #check and validate session id
    session = get_session(answerReq.session_id)

    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    if session.started_at is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="start the interview before submitting an answer")

    time_remaining = remaining_seconds(session)
    if time_remaining == 0:
        complete_session(session)
        session.report = await generate_report(session.answers, session.job_title)
        return {"InterviewEnded": True, "remainingSeconds": 0, "report": session.report}

    save_answer(answerReq.answer, answerReq.skip, session)
    time_remaining = remaining_seconds(session)
    if time_remaining == 0:
        complete_session(session)
        session.report = await generate_report(session.answers, session.job_title)
        return {"InterviewEnded": True, "remainingSeconds": 0, "report": session.report}

    next_turn = await generate_next_turn(
        job_title=session.job_title,
        job_description=session.job_description,
        resume_text=session.resume_text,
        answers=session.answers,
        current_question=session.current_question,
        follow_ups_on_topic=session.follow_ups_on_topic,
        remaining_time=time_remaining,
    )
    session.answers[-1].assessment = next_turn.get("assessment")
    question_type = next_turn.get("question_type", "new_topic")
    next_question = next_turn.get("next_question")
    if not isinstance(next_question, str) or not next_question.strip():
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI could not generate the next interview question")
    if question_type == "follow_up":
        session.follow_ups_on_topic += 1
    else:
        session.follow_ups_on_topic = 0
    session.current_question = next_question.strip()

    time_remaining = remaining_seconds(session)
    if time_remaining == 0:
        complete_session(session)
        session.report = await generate_report(session.answers, session.job_title)
        return {"InterviewEnded": True, "remainingSeconds": 0, "report": session.report}

    return {
        "InterviewEnded": False,
        "nextQuestion": session.current_question,
        "interviewerResponse": next_turn.get("acknowledgment"),
        "questionType": question_type,
        "remainingSeconds": time_remaining,
    }

@router.put("/end/{session_id}")
async def end_interview(session_id: str):
    #check and validate session id
    session = get_session(session_id)

    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    complete_session(session)
    session.report = await generate_report(session.answers, session.job_title)

    return {
        "InterviewEnded": True,
        "report": session.report,
    }

@router.get("/report/{session_id}")
async def report(session_id: str):
    #check and validate session id
    session = get_session(session_id)

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    if session.started_at is not None and remaining_seconds(session) == 0:
        complete_session(session)
    if session.status == InterviewStatusEnum.COMPLETED:
        if session.report is None:
            session.report = await generate_report(session.answers, session.job_title)
        report_result = session.report
    else:
        report_result = await generate_report(session.answers, session.job_title)

    return {"result": report_result}

