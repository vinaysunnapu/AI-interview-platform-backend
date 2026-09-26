from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models.interview import InterviewStatusEnum
from request_model.AnswerRequest import AnswerRequest
from response_model.AnswerResponse import AnswerResponse
from services.ai_service import generate_questions_intro, generate_report
from services.interview_service import create_session, get_session, save_answer
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

    session = create_session()
    session.questions = resp.get("questions")
    session.introText = resp.get("introText")

    print("Result >>", resp)

    return {
    "session_id": str(session.session_id)
}

@router.get("/start/{session_id}")
async def start_interview(session_id: str):
    #check and validate session id
    session = get_session(session_id)

    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    return {
        "introText": session.introText,
        "firstQuestion": session.questions[0]
    }

@router.post("/submit", response_model= AnswerResponse)
async def submit_answer(answerReq: AnswerRequest):
    #check and validate session id
    session = get_session(answerReq.session_id)

    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    # save answer in interview session
    save_answer(answerReq.answer, answerReq.skip, session)

    if session.status == InterviewStatusEnum.COMPLETED:
        return {
            "InterviewEnded": True
        }
    return {
        "InterviewEnded": False,
        "nextQuestion": session.questions[session.current_idx]
    }

@router.put("/end/{session_id}")
async def end_interview(session_id: str):
    #check and validate session id
    session = get_session(session_id)

    if not session or session.status == InterviewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    session.status = InterviewStatusEnum.COMPLETED

    return {
        "InterviewEnded": True,
    }

@router.get("/report/{session_id}")
async def report(session_id: str):
    #check and validate session id
    session = get_session(session_id)

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="interview session notfound")

    resp = await generate_report(session.answers)

    return {"result": resp}

