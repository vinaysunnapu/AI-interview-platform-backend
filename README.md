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

- `POST /interview/generate_question`: multipart form fields `job_title`, `job_description`, and `resume` (PDF only, up to 5 MB); prepares an interview session and returns a `session_id`.
- `GET /interview/start/{session_id}`: starts the 10-minute timer and returns the introduction, first question, and remaining time.
- `POST /interview/submit`: JSON body with `session_id`, `answer`, and `skip`; evaluates the answer and returns a contextual follow-up or a new topic. At timeout, the response includes the final report.
- `PUT /interview/end/{session_id}`: ends the interview early and returns the final report.
- `GET /interview/report/{session_id}`: returns the cached final report, or generates one from all answers if needed.

Questions after the opening question are generated dynamically from the candidate's answers. The interview moves between follow-ups and new topics until the 10-minute timer expires or the candidate ends it.

## Notes

- Interview sessions are held in process memory, so they are lost when the server restarts and are not shared between multiple workers.
- CORS currently allows all origins in `main.py`; restrict this to the frontend origin before deploying publicly.