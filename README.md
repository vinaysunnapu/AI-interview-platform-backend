# AI Interview Backend

A FastAPI backend that generates interview questions from a job description and a candidate's PDF resume, records answers, and generates an interview report using the Groq API.

## Requirements

- Python 3.10 or newer
- A Groq API key

## Setup on Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your key:

```env
GROQ_API_KEY=your_actual_groq_api_key
```

Keep `.env` private. It is excluded from Git; commit `.env.example` instead.

## Run

```powershell
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## API

- `POST /interview/generate_question`: multipart form fields `job_title`, `job_description`, and `resume` (PDF only, up to 5 MB); returns a `session_id`.
- `GET /interview/start/{session_id}`: returns the introduction and first question.
- `POST /interview/submit`: JSON body with `session_id`, `answer`, and `skip`; records an answer and returns the next question or indicates the interview ended.
- `PUT /interview/end/{session_id}`: ends an interview session.
- `GET /interview/report/{session_id}`: generates a report from the session's answers.

## Notes

- Interview sessions are held in process memory, so they are lost when the server restarts and are not shared between multiple workers.
- CORS currently allows all origins in `main.py`; restrict this to the frontend origin before deploying publicly.