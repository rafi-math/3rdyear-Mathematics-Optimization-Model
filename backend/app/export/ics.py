"""Hand-written ICS calendar exporter."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Dict


def format_ics_datetime(dt: datetime) -> str:
    """Format floating local datetime for ICS (YYYYMMDDTHHMMSS)."""
    return dt.strftime("%Y%m%dT%H%M%S")


def generate_ics(data: Dict[str, Any]) -> bytes:
    """Generate RFC 5545 compliant iCalendar string for study sessions."""
    model_choice = data.get("model", "B")
    results = data.get("results", {})
    model_res = results.get(model_choice, {})
    allocations = model_res.get("allocations", [])

    # Start date and time
    start_date_str = data.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    start_time_str = data.get("start_time", "09:00")  # HH:MM

    try:
        current_dt = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
    except Exception:
        current_dt = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Study Budget Optimizer//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    schedule = data.get("schedule")
    if schedule:
        # Multi-period schedule
        for period_idx, p_sched in enumerate(schedule):
            p_label = p_sched.get("period_label", f"Period {period_idx + 1}")
            p_dt = current_dt + timedelta(days=period_idx)
            block_dt = p_dt
            for cname, mins in p_sched.get("allocations", {}).items():
                if mins <= 0.5:
                    continue
                duration = timedelta(minutes=round(mins))
                end_dt = block_dt + duration
                uid = f"{uuid.uuid4()}@studyoptimizer"
                lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{format_ics_datetime(datetime.now(timezone.utc))}Z",
                    f"DTSTART:{format_ics_datetime(block_dt)}",
                    f"DTEND:{format_ics_datetime(end_dt)}",
                    f"SUMMARY:Study: {cname}",
                    f"DESCRIPTION:Allocated {round(mins)} minutes ({p_label}) under Model {model_choice}.",
                    "END:VEVENT",
                ])
                block_dt = end_dt
    else:
        # Single period / weekly blocks
        block_dt = current_dt
        for alloc in allocations:
            mins = alloc.get("minutes", 0.0)
            if mins <= 0.5:
                continue
            cname = alloc.get("course_name", "Course")
            duration = timedelta(minutes=round(mins))
            end_dt = block_dt + duration
            uid = f"{uuid.uuid4()}@studyoptimizer"
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{format_ics_datetime(datetime.now(timezone.utc))}Z",
                f"DTSTART:{format_ics_datetime(block_dt)}",
                f"DTEND:{format_ics_datetime(end_dt)}",
                f"SUMMARY:Study: {cname}",
                f"DESCRIPTION:Allocated {round(mins)} minutes under Model {model_choice}.",
                "END:VEVENT",
            ])
            block_dt = end_dt

    lines.append("END:VCALENDAR")
    lines.append("")
    # CRLF line endings per RFC 5545
    return "\r\n".join(lines).encode("utf-8")
