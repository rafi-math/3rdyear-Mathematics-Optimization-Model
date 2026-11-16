"""Template-based explanation generator comparing allocations between models."""
from __future__ import annotations

from typing import Dict, List
from app.schemas import ModelResult, Plan


def format_minutes_text(minutes: float) -> str:
    """Format minutes into human-readable text like '1 h 10 m' or '56 min'."""
    m = round(minutes)
    if m >= 60:
        h = m // 60
        rem = m % 60
        return f"{h} h {rem} m" if rem > 0 else f"{h} h"
    return f"{m} min"


def generate_explanations(plan: Plan, results: Dict[str, ModelResult]) -> List[str]:
    """Compare plans and generate plain-English sentences."""
    explanations: List[str] = []

    # 1. Compare credits-only plan vs credits+difficulty plan
    if "A" in results and "B" in results:
        res_a = results["A"]
        res_b = results["B"]
        alloc_a = {a.course_name: a.minutes for a in res_a.allocations}
        alloc_b = {b.course_name: b.minutes for b in res_b.allocations}
        status_b = {b.course_name: b.status for b in res_b.allocations}

        diffs = []
        for name in alloc_a:
            val_a = alloc_a[name]
            val_b = alloc_b.get(name, 0.0)
            diff = val_b - val_a
            if abs(diff) >= 5.0:
                diffs.append((abs(diff), diff, name, val_a, val_b))

        diffs.sort(key=lambda x: x[0], reverse=True)

        if diffs:
            sentences = []
            for _, diff, name, val_a, val_b in diffs[:3]:
                time_a = format_minutes_text(val_a)
                time_b = format_minutes_text(val_b)
                stat = status_b.get(name, "")
                if diff > 0:
                    if stat == "at_minimum":
                        cause = "It gets at least the minimum time you set."
                    elif stat == "locked":
                        cause = "You fixed this time in your plan."
                    else:
                        cause = "You marked it as harder or gave it higher priority, so it gets more time."
                    sentences.append(f"{name} gets {time_b} when difficulty is included, compared to {time_a} when only credits are used. {cause}")
                else:
                    if stat == "at_minimum":
                        cause = "It stays at the minimum time you set."
                    elif stat == "locked":
                        cause = "You fixed this time in your plan."
                    else:
                        cause = "Other courses take more priority in this plan."
                    sentences.append(f"{name} goes down from {time_a} to {time_b} when difficulty is included. {cause}")
            explanations.append(" ".join(sentences))
        else:
            explanations.append("Including difficulty does not change the plan much because your course priorities are very similar.")

    # 2. Compare credits+difficulty plan vs plan with breaks/diminishing returns
    if "B" in results and "C" in results:
        res_b = results["B"]
        res_c = results["C"]
        alloc_b = {b.course_name: b.minutes for b in res_b.allocations}
        alloc_c = {c.course_name: c.minutes for c in res_c.allocations}

        diffs = []
        for name in alloc_b:
            val_b = alloc_b[name]
            val_c = alloc_c.get(name, 0.0)
            diff = val_c - val_b
            if abs(diff) >= 5.0:
                diffs.append((abs(diff), diff, name, val_b, val_c))

        diffs.sort(key=lambda x: x[0], reverse=True)

        if diffs:
            sentences = []
            for _, diff, name, val_b, val_c in diffs[:3]:
                time_b = format_minutes_text(val_b)
                time_c = format_minutes_text(val_c)
                if diff > 0:
                    sentences.append(f"{name} increases from {time_b} to {time_c} when the plan spreads time more evenly across courses.")
                else:
                    sentences.append(f"{name} drops from {time_b} to {time_c} when the plan avoids putting too much time into one course.")
            explanations.append(" ".join(sentences))
        else:
            explanations.append("The plan with more even spreading gives a similar result for your current settings.")

    return explanations
