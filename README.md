# Study budget

A tool that takes a student's courses (name, credits, difficulty), a time budget and any personal rules, and returns how many minutes or hours each course should get. It runs three optimisation models side by side and explains in plain terms why they differ.

The research behind it is a single case study from a published paper (*Optimising a Scarce Study Budget*, Md. Ali Arman Rafi). The tool itself works for any student, any number of courses and any time horizon.

## Stack

| Layer | Choice |
|---|---|
| Front end | Vite + React 19 + TypeScript, plain CSS with custom properties |
| Charts | D3 scales rendered into SVG by React |
| Back end | Python 3.13, FastAPI, Pydantic v2 |
| Solver | `scipy.optimize.linprog` (HiGHS). PuLP with CBC for parity tests |
| Parser | Gemini API through a provider interface (mock provider used when no key is set) |
| Document extraction | `pypdf` for PDF text, `python-docx` for DOCX |
| Exports | `csv` module, `reportlab` for PDF, RFC 5545 `.ics` |
| Tests | `pytest`, `hypothesis` for property tests, Playwright for end-to-end checks |

## Local setup

### Prerequisites

- Python 3.13 or later
- Node.js 20 or later
- npm 10 or later

### Backend

```bash
cd backend
py -3.13 -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your GEMINI_API_KEY if you want AI parsing.
# The solver works without it.

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Running tests

### Backend (14 tests)

```bash
cd <project root>
$env:PYTHONPATH='backend'                          # PowerShell
# export PYTHONPATH=backend                        # bash
backend\.venv\Scripts\pytest backend\tests -v
```

### Frontend build check

```bash
cd frontend
npm run build
```

### End-to-end (Playwright, 5 tests)

```bash
cd frontend
npx playwright install chromium
npx playwright test
```

Playwright starts both the backend and frontend dev servers automatically.

### Copy and design audit

```bash
cd <project root>
$env:PYTHONPATH='backend'
backend\.venv\Scripts\python backend\tests\audit_copy_design.py
```

## Docker (backend only)

```bash
cd backend
docker build -t study-budget-api .
docker run -p 8000:8000 --env-file .env study-budget-api
```

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | (none) | Gemini API key for multimodal parsing. Leave blank to use the mock provider |
| `PARSER_MODEL` | `gemini-2.5-flash` | Which Gemini model the parser calls |
| `ALLOWED_ORIGIN` | `http://localhost:5173` | CORS origin for the frontend |
| `MAX_UPLOAD_MB` | `10` | Maximum upload size in megabytes |

## Out of scope for v1

Accounts, saved plans on a server, notifications, sharing links, dark mode, languages other than English, a mobile app, minimum session length in scheduling.
