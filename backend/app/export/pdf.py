"""Native ReportLab one-page A4 PDF exporter following Swiss editorial design."""
from __future__ import annotations

from datetime import datetime
import io
from typing import Any, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line


INK = colors.HexColor("#111111")
INK2 = colors.HexColor("#4A4A46")
PAPER = colors.HexColor("#F5F3EE")
PAPER2 = colors.HexColor("#ECE9E1")
ACCENT = colors.HexColor("#CC3300")
RULE_SOFT = colors.HexColor("#CFCBC0")
SERIES_C = colors.HexColor("#8A8578")


def generate_pdf(data: Dict[str, Any]) -> bytes:
    """Generate a clean single-page A4 PDF with Swiss editorial typography."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SwissTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=INK,
    )
    meta_style = ParagraphStyle(
        "SwissMeta",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9,
        leading=12,
        textColor=INK2,
    )
    body_style = ParagraphStyle(
        "SwissBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=INK,
    )
    body_bold = ParagraphStyle(
        "SwissBodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=INK,
    )

    story = []

    # Title & Header
    story.append(Paragraph("STUDY BUDGET OPTIMISATION", title_style))
    today_str = datetime.now().strftime("%d %B %Y")
    plan = data.get("plan", {})
    budget_mins = plan.get("budget", {}).get("amount_minutes", 0)
    story.append(
        Paragraph(
            f"REPORT GENERATED {today_str.upper()} &bull; HORIZON BUDGET: {budget_mins:.0f} MIN",
            meta_style,
        )
    )
    story.append(Spacer(1, 10))

    # Allocation Table Data
    results = data.get("results", {})
    courses = plan.get("courses", [])

    res_a = results.get("A", {})
    res_b = results.get("B", {})
    res_c = results.get("C", {})

    allocs_a = {a["course_name"]: a.get("minutes", 0.0) for a in res_a.get("allocations", [])}
    allocs_b = {b["course_name"]: b.get("minutes", 0.0) for b in res_b.get("allocations", [])}
    allocs_c = {c["course_name"]: c.get("minutes", 0.0) for c in res_c.get("allocations", [])}

    table_data = [
        [
            Paragraph("<b>COURSE</b>", meta_style),
            Paragraph("<b>CR</b>", meta_style),
            Paragraph("<b>DIFF</b>", meta_style),
            Paragraph("<b>A (MIN)</b>", meta_style),
            Paragraph("<b>B (MIN)</b>", meta_style),
            Paragraph("<b>C (MIN)</b>", meta_style),
        ]
    ]

    for c in courses:
        cname = c.get("name", "")
        cr = str(c.get("credits", ""))
        diff = (c.get("difficulty_level") or str(c.get("custom_difficulty", ""))).replace("_", " ").capitalize()
        table_data.append([
            Paragraph(cname, body_style),
            Paragraph(cr, body_style),
            Paragraph(diff, body_style),
            Paragraph(f"{allocs_a.get(cname, 0.0):.1f}", body_style),
            Paragraph(f"{allocs_b.get(cname, 0.0):.1f}", body_style),
            Paragraph(f"{allocs_c.get(cname, 0.0):.1f}", body_style),
        ])

    # Totals row
    table_data.append([
        Paragraph("<b>Total</b>", body_bold),
        Paragraph(f"<b>{sum(c.get('credits', 0) for c in courses)}</b>", body_bold),
        Paragraph("", body_style),
        Paragraph(f"<b>{res_a.get('total_minutes', 0.0):.1f}</b>", body_bold),
        Paragraph(f"<b>{res_b.get('total_minutes', 0.0):.1f}</b>", body_bold),
        Paragraph(f"<b>{res_c.get('total_minutes', 0.0):.1f}</b>", body_bold),
    ])

    col_widths = [190, 35, 75, 70, 70, 70]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(
        TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 1, INK),
            ("LINEBELOW", (0, 0), (-1, 0), 1, INK),
            ("LINEBELOW", (0, 1), (-1, -2), 0.5, RULE_SOFT),
            ("LINEABOVE", (0, -1), (-1, -1), 1.5, INK),
            ("LINEBELOW", (0, -1), (-1, -1), 1, INK),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )
    story.append(t)
    story.append(Spacer(1, 14))

    # Native ReportLab Horizontal Bar Chart
    # Plot top courses or up to 10 courses for Model B vs A
    chart_courses = courses[:10]
    num_chart_courses = len(chart_courses)
    row_height = 18
    chart_height = num_chart_courses * row_height + 25
    chart_width = 510
    draw = Drawing(chart_width, chart_height)

    # Find max allocation for scale
    max_val = max([allocs_b.get(c.get("name"), 0) for c in chart_courses] + [80.0])
    bar_scale = (chart_width - 180) / (max_val * 1.1)

    # Chart header
    draw.add(String(0, chart_height - 10, "ALLOCATION COMPARISON (MODEL A vs B)", fontName="Courier-Bold", fontSize=8, fillColor=INK))
    draw.add(Rect(320, chart_height - 12, 10, 6, fillColor=INK, strokeColor=None))
    draw.add(String(335, chart_height - 10, "Model A", fontName="Helvetica", fontSize=8, fillColor=INK))
    draw.add(Rect(410, chart_height - 12, 10, 6, fillColor=ACCENT, strokeColor=None))
    draw.add(String(425, chart_height - 10, "Model B", fontName="Helvetica", fontSize=8, fillColor=INK))

    for idx, c in enumerate(chart_courses):
        cname = c.get("name", "")
        display_name = cname[:22] + ".." if len(cname) > 24 else cname
        y = chart_height - 25 - (idx + 1) * row_height

        draw.add(String(0, y + 4, display_name, fontName="Helvetica", fontSize=8, fillColor=INK))

        val_a = allocs_a.get(cname, 0.0)
        val_b = allocs_b.get(cname, 0.0)

        w_a = val_a * bar_scale
        w_b = val_b * bar_scale

        # Model A bar
        draw.add(Rect(160, y + 6, max(1, w_a), 4, fillColor=INK, strokeColor=None))
        # Model B bar
        draw.add(Rect(160, y + 1, max(1, w_b), 4, fillColor=ACCENT, strokeColor=None))

    story.append(draw)
    story.append(Spacer(1, 12))

    # Sensitivity & Shadow Price Sentence
    sp_val = res_b.get("shadow_price") or res_a.get("shadow_price") or 3.0
    next_courses = res_b.get("next_hour_courses") or ["priority subjects"]
    next_str = ", ".join(next_courses)
    sp_text = (
        f"<b>Value of one more hour:</b> One more hour, spent where it counts most, adds {sp_val:.1f} to the objective. "
        f"That is a score inside this model. It is not marks or CGPA. The next hour would go to: {next_str}."
    )
    story.append(Paragraph(sp_text, body_style))
    story.append(Spacer(1, 8))

    delta_check = res_b.get("shadow_price_delta_check")
    if delta_check is not None:
        chk_text = (
            f"Check: re-solving with 30 more minutes changes the objective by {delta_check * 0.5:.2f}, "
            f"which is {delta_check:.1f} per hour."
        )
        story.append(Paragraph(chk_text, meta_style))

    doc.build(story)
    return buffer.getvalue()
