from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.analyzer.parsers import extract_text_from_bytes
from app.analyzer.analyze import analyze_resume_text

app = FastAPI(title="Resume Analyzer")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze")
async def analyze(
    request: Request,
    resume_file: Optional[UploadFile] = File(default=None),
    resume_text: Optional[str] = Form(default=None),
    job_description: Optional[str] = Form(default=None),
):
    try:
        text: Optional[str] = None

        if resume_file is not None:
            data = await resume_file.read()
            text = extract_text_from_bytes(resume_file.filename or "uploaded", data)
        elif resume_text is not None:
            text = resume_text

        if text is None or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Please upload a file or paste your resume text.")

        analysis = analyze_resume_text(text, job_description or "")
        return JSONResponse(content=analysis)
    except HTTPException:
        raise
    except Exception as exc:
        # Log in real systems
        return JSONResponse(status_code=500, content={"error": str(exc)})