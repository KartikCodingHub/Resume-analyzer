# Resume Analyzer

A modern, professional website that helps users analyze their resumes using AI-inspired heuristics. Upload a PDF/DOCX/TXT or paste your resume text, optionally include a job description, and get an ATS-style score, keyword coverage, readability insights, skills extraction, and concrete improvement suggestions.

## Features
- Modern UI (Tailwind CDN) with drag-and-drop upload or paste
- PDF, DOCX, and TXT parsing
- ATS-style overall score and sub-scores (structure, keywords, clarity, length, ATS-friendliness)
- Keyword coverage against a provided job description
- Readability insights
- Skills extraction (common tech/business skills)
- Actionable suggestions and warnings
- Fully local by default; no external AI key required

## Tech Stack
- FastAPI (backend, JSON API)
- Jinja2 (server-rendered index)
- Tailwind (via CDN) for styling
- PyPDF2, python-docx, textstat for parsing and readability

## Quickstart

1) Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Run the development server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4) Open the app

- Visit http://localhost:8000 in your browser

## Optional: Enhance with an LLM
This app ships with strong heuristic analysis that runs fully locally. If you wish to add an LLM step for extra suggestions, you can:

- `pip install openai`
- Set `OPENAI_API_KEY` in your environment

If the key and library are available, the backend will use the LLM to enrich suggestions (best-effort, optional).

## Notes
- Keep your resume under ~2 pages for best scores
- For PDF parsing, text extraction depends on how the PDF was generated (native text vs image). If your PDF is image-based, convert to text or upload DOCX/TXT.
- This tool does not store uploads; all processing is in-memory.