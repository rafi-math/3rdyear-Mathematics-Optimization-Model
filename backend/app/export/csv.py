"""CSV export generator for allocations and constraints with UTF-8 BOM."""
from __future__ import annotations

import csv
import io
from typing import Any, Dict


def generate_csv(data: Dict[str, Any]) -> bytes:
    """Generate CSV with course allocations across models and constraint breakdown."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Course",
        "Credits",
        "Difficulty",
        "Model A (min)",
        "Model B (min)",
        "Model C (min)",
        "Status A",
        "Status B",
        "Status C",
    ])

    results = data.get("results", {})
    plan = data.get("plan", {})
    courses = plan.get("courses", [])

    res_a = results.get("A", {})
    res_b = results.get("B", {})
    res_c = results.get("C", {})

    allocs_a = {a["course_name"]: a for a in res_a.get("allocations", [])}
    allocs_b = {b["course_name"]: b for b in res_b.get("allocations", [])}
    allocs_c = {c["course_name"]: c for c in res_c.get("allocations", [])}

    for c in courses:
        cname = c.get("name", "")
        credits = c.get("credits", "")
        diff = c.get("difficulty_level") or c.get("custom_difficulty", "")

        a_data = allocs_a.get(cname, {})
        b_data = allocs_b.get(cname, {})
        c_data = allocs_c.get(cname, {})

        writer.writerow([
            cname,
            credits,
            diff,
            f"{a_data.get('minutes', 0.0):.1f}" if a_data else "",
            f"{b_data.get('minutes', 0.0):.1f}" if b_data else "",
            f"{c_data.get('minutes', 0.0):.1f}" if c_data else "",
            a_data.get("status", ""),
            b_data.get("status", ""),
            c_data.get("status", ""),
        ])

    # Totals row
    writer.writerow([
        "Total",
        sum(c.get("credits", 0) for c in courses),
        "",
        f"{res_a.get('total_minutes', 0.0):.1f}" if res_a else "",
        f"{res_b.get('total_minutes', 0.0):.1f}" if res_b else "",
        f"{res_c.get('total_minutes', 0.0):.1f}" if res_c else "",
        "",
        "",
        "",
    ])

    writer.writerow([])  # Blank line

    # Constraints section
    writer.writerow(["Constraint Status", "Model", "Description", "Slack (min)", "Binding"])
    for m_key in ("A", "B", "C"):
        m_res = results.get(m_key, {})
        for constr in m_res.get("constraints", []):
            writer.writerow([
                constr.get("name", ""),
                f"Model {m_key}",
                constr.get("description", ""),
                f"{constr.get('slack_minutes', 0.0):.1f}",
                "Yes" if constr.get("is_binding") else "No",
            ])

    # UTF-8 with BOM for Excel
    csv_str = output.getvalue()
    return "\ufeff".encode("utf-8") + csv_str.encode("utf-8")
