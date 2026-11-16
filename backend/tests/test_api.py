"""FastAPI integration tests for health, case-study, solve, and exports."""
from __future__ import annotations

import json
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "case-study.json"


def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_api_case_study():
    res = client.get("/case-study")
    assert res.status_code == 200
    data = res.json()
    assert "courses" in data
    assert len(data["courses"]) == 10
    assert data["budget"]["amount_minutes"] == 456


def test_api_solve_case_study():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    res = client.post("/solve", json={"plan": plan_data, "models": ["A", "B", "C"]})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "optimal"
    assert "A" in body["results"]
    assert "B" in body["results"]
    assert "C" in body["results"]
    assert abs(body["results"]["A"]["total_minutes"] - 456.0) < 1e-4
    assert abs(body["results"]["B"]["total_minutes"] - 456.0) < 1e-4
    assert len(body["explanations"]) >= 1


def test_api_solve_infeasible():
    # Infeasible: floor > budget
    plan_data = {
        "courses": [
            {"name": "Math", "credits": 3, "difficulty_level": "medium", "min_minutes": 100},
            {"name": "Physics", "credits": 3, "difficulty_level": "medium", "min_minutes": 100},
        ],
        "budget": {"mode": "weekly", "amount_minutes": 150},
        "settings": {"min_minutes_per_course": 20},
    }
    res = client.post("/solve", json={"plan": plan_data, "models": ["B"]})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "infeasible"
    assert len(body["reasons"]) > 0


def test_api_exports():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    solve_res = client.post("/solve", json={"plan": plan_data, "models": ["A", "B", "C"]}).json()
    payload = {"plan": plan_data, "results": solve_res["results"], "model": "B"}

    csv_res = client.post("/export/csv", json=payload)
    assert csv_res.status_code == 200
    assert csv_res.headers["content-type"].startswith("text/csv")

    pdf_res = client.post("/export/pdf", json=payload)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"].startswith("application/pdf")

    ics_res = client.post("/export/ics", json=payload)
    assert ics_res.status_code == 200
    assert ics_res.headers["content-type"].startswith("text/calendar")
