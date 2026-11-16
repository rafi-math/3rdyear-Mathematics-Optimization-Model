"""Tests for CSV, PDF, and ICS export generators (Test 9)."""
from __future__ import annotations

import io
import json
from pathlib import Path
import pypdf
import icalendar

from app.schemas import Plan
from app.solver.models import build_model_result
from app.export.csv import generate_csv
from app.export.pdf import generate_pdf
from app.export.ics import generate_ics

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "case-study.json"


def test_9_exports_csv_ics_pdf():
    """CSV has correct columns, ICS parses with icalendar, PDF is exactly one page."""
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    plan = Plan(**data)
    res_a = build_model_result(plan, "A")
    res_b = build_model_result(plan, "B")
    res_c = build_model_result(plan, "C")

    payload = {
        "plan": plan.model_dump(),
        "results": {
            "A": res_a.model_dump(),
            "B": res_b.model_dump(),
            "C": res_c.model_dump(),
        },
        "model": "B",
    }

    # 1. Test CSV
    csv_bytes = generate_csv(payload)
    assert csv_bytes.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM
    csv_text = csv_bytes.decode("utf-8-sig")
    lines = [l.strip() for l in csv_text.strip().split("\n")]
    assert "Course,Credits,Difficulty,Model A (min),Model B (min),Model C (min)" in lines[0]
    assert any("Real Analysis (II)" in line for line in lines)
    assert any("Constraint Status" in line for line in lines)

    # 2. Test ICS
    ics_bytes = generate_ics(payload)
    cal = icalendar.Calendar.from_ical(ics_bytes)
    assert cal.get("PRODID") is not None
    events = [sub for sub in cal.subcomponents if sub.name == "VEVENT"]
    assert len(events) == len(plan.courses)
    assert "Study: Real Analysis (II)" in [str(ev.get("SUMMARY")) for ev in events]

    # 3. Test PDF (exactly one page)
    pdf_bytes = generate_pdf(payload)
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) == 1, f"Expected 1 page, got {len(reader.pages)}"
