"""
Generates a downloadable PDF report containing the user's profile,
health calculations, and generated fitness/nutrition plan.
"""
import re
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

GREEN = colors.HexColor("#16A34A")
BLUE = colors.HexColor("#2563EB")
DARK = colors.HexColor("#111827")
GRAY = colors.HexColor("#6B7280")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="FitTitle", fontSize=24, textColor=GREEN,
                               spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="FitSubtitle", fontSize=11, textColor=GRAY,
                               spaceAfter=16))
    styles.add(ParagraphStyle(name="FitH2", fontSize=15, textColor=BLUE,
                               spaceBefore=14, spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="FitBody", fontSize=10, textColor=DARK,
                               leading=14))
    return styles


def _markdown_to_flowables(md_text: str, styles):
    """Very small markdown -> platypus converter: handles #/##, tables, bullets, bold."""
    flowables = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.startswith("## "):
            flowables.append(Paragraph(_inline(line[3:]), styles["FitH2"]))
            i += 1
            continue
        if line.startswith("# "):
            flowables.append(Paragraph(_inline(line[2:]), styles["FitTitle"]))
            i += 1
            continue

        # Markdown table detection
        if line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = [
                [c.strip() for c in row.strip("|").split("|")]
                for row in table_lines
                if not set(row.replace("|", "").replace("-", "").strip()) == set()
            ]
            # drop markdown separator row (---|---)
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            if rows:
                data = [[Paragraph(_inline(c), styles["FitBody"]) for c in row] for row in rows]
                t = Table(data, hAlign="LEFT", repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ]))
                flowables.append(t)
                flowables.append(Spacer(1, 10))
            continue

        if line.strip().startswith(("-", "*")):
            flowables.append(Paragraph("&bull; " + _inline(line.strip()[1:].strip()), styles["FitBody"]))
            i += 1
            continue

        flowables.append(Paragraph(_inline(line), styles["FitBody"]))
        flowables.append(Spacer(1, 4))
        i += 1

    return flowables


def _inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def generate_report_pdf(user: dict, calc: dict, plan_markdown: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = _styles()
    flow = []

    flow.append(Paragraph("FitAI — Personalized Fitness Report", styles["FitTitle"]))
    flow.append(Paragraph(f"Prepared for {user['name']}", styles["FitSubtitle"]))

    profile_rows = [
        ["Age", str(user["age"]), "Gender", user["gender"]],
        ["Height", f"{user['height_cm']} cm", "Weight", f"{user['weight_kg']} kg"],
        ["Target Weight", f"{user['target_weight_kg']} kg", "Goal", user["goal"].replace("_", " ").title()],
        ["Diet Type", user["diet_type"].replace("_", " ").title(), "Activity Level", user["activity_level"].replace("_", " ").title()],
    ]
    pt = Table(profile_rows, hAlign="LEFT", colWidths=[3.5 * cm, 4 * cm, 3.5 * cm, 4 * cm])
    pt.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), GRAY),
        ("TEXTCOLOR", (2, 0), (2, -1), GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
    ]))
    flow.append(pt)
    flow.append(Spacer(1, 12))

    flow.append(Paragraph("Health Metrics", styles["FitH2"]))
    metric_rows = [
        ["BMI", f"{calc['bmi']} ({calc['bmi_category']})"],
        ["BMR", f"{calc['bmr']} kcal/day"],
        ["TDEE", f"{calc['tdee']} kcal/day"],
        ["Daily Calorie Target", f"{calc['daily_calories']} kcal"],
        ["Protein", f"{calc['protein_g']} g"],
        ["Carbohydrates", f"{calc['carbs_g']} g"],
        ["Fat", f"{calc['fat_g']} g"],
        ["Water Intake", f"{calc['water_l']} L/day"],
    ]
    mt = Table(metric_rows, hAlign="LEFT", colWidths=[6 * cm, 6 * cm])
    mt.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FDF4")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    flow.append(mt)
    flow.append(PageBreak())

    flow.append(Paragraph("Your Personalized Plan", styles["FitTitle"]))
    flow.extend(_markdown_to_flowables(plan_markdown or "_No plan generated yet._", styles))

    doc.build(flow)
    return buf.getvalue()
