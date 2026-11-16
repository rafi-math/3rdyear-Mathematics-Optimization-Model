"""FastAPI backend application for the study optimizer."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    Course,
    Plan,
    ParsedPlan,
    SolveRequest,
    SolveResponse,
)
from app.solver.diagnose import check_cheap_infeasibility, diagnose_infeasibility
from app.solver.models import build_model_result
from app.solver.schedule import schedule_multi_period
from app.explain import generate_explanations

app = FastAPI(title="Study Budget Optimizer API", version="1.0.0")

# CORS setup
allowed_origins_env = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")
origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
if "*" not in origins and "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}


@app.get("/case-study")
@app.get("/api/v1/case-study")
def get_case_study():
    fixture_path = FIXTURES_DIR / "case-study.json"
    if not fixture_path.exists():
        raise HTTPException(status_code=404, detail="Case study fixture not found.")
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/solve", response_model=SolveResponse)
@app.post("/api/v1/solve", response_model=SolveResponse)
def solve_endpoint(req: SolveRequest):
    plan = req.plan
    models_to_run = req.models or ["A", "B", "C"]

    # First check cheap feasibility
    cheap_diag = check_cheap_infeasibility(plan, model_type="B")
    if cheap_diag is not None:
        return SolveResponse(
            status="infeasible",
            reasons=cheap_diag["reasons"],
            suggestions=cheap_diag["suggestions"],
        )

    results = {}
    for m in models_to_run:
        try:
            res = build_model_result(plan, m)
            results[m] = res
        except Exception as e:
            # Check if it was solver infeasibility
            infeas_diag = diagnose_infeasibility(plan, model_type=m)
            if infeas_diag["reasons"]:
                return SolveResponse(
                    status="infeasible",
                    reasons=infeas_diag["reasons"],
                    suggestions=infeas_diag["suggestions"],
                )
            raise HTTPException(status_code=400, detail=f"Solver error in Model {m}: {str(e)}")

    explanations = generate_explanations(plan, results)

    # Optional multi-period scheduling
    schedule = None
    if plan.budget.mode in ("custom", "daily"):
        # Use Model B allocations as reference for schedule if available, else first model
        ref_model = "B" if "B" in results else models_to_run[0]
        totals = {a.course_name: a.minutes for a in results[ref_model].allocations}
        try:
            schedule = schedule_multi_period(plan, totals)
        except Exception as e:
            # Non-fatal, return results without schedule
            pass

    return SolveResponse(
        status="optimal",
        results=results,
        explanations=explanations,
        schedule=schedule,
    )


# Multimodal parser endpoint
@app.post("/parse", response_model=ParsedPlan)
@app.post("/api/v1/parse", response_model=ParsedPlan)
async def parse_endpoint(
    text: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
    from app.parse.provider import parse_input_multimodal

    max_mb = float(os.getenv("MAX_UPLOAD_MB", "10"))
    file_payloads = []
    if files:
        for f in files:
            content = await f.read()
            if len(content) > max_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail=f"That file is over {int(max_mb)} MB.",
                )
            file_payloads.append((f.filename or "unknown", f.content_type or "", content))

    try:
        parsed = await parse_input_multimodal(text=text, files=file_payloads)
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read that. Paste the text instead, or enter the courses by hand.",
        )


# Export endpoints
@app.post("/export/csv")
@app.post("/api/v1/export/csv")
def export_csv_endpoint(data: dict):
    from app.export.csv import generate_csv

    csv_bytes = generate_csv(data)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="study-budget.csv"'},
    )


@app.post("/export/pdf")
@app.post("/api/v1/export/pdf")
def export_pdf_endpoint(data: dict):
    from app.export.pdf import generate_pdf

    pdf_bytes = generate_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="study-budget.pdf"'},
    )


@app.post("/export/ics")
@app.post("/api/v1/export/ics")
def export_ics_endpoint(data: dict):
    from app.export.ics import generate_ics

    ics_bytes = generate_ics(data)
    return Response(
        content=ics_bytes,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="study-budget.ics"'},
    )
