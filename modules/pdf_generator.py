"""
pdf_generator.py
----------------
Generates a downloadable, professional PDF report using ReportLab.

The report includes:
    - Student details
    - Semester-wise table
    - Current CGPA & Percentage
    - Target CGPA & required future SGPA
    - AI Advisor recommendations
    - Performance charts (SGPA trend, semester performance, credit distribution)
"""

import os
import tempfile
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    ListFlowable,
    ListItem,
)
from reportlab.lib.enums import TA_CENTER

from modules import graphs

PRIMARY_COLOR = colors.HexColor("#2E5EAA")
LIGHT_GRID = colors.HexColor("#EAEFF7")


def _build_styles():
    """Create and return the paragraph styles used throughout the report."""
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            fontSize=20,
            leading=24,
            textColor=PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            fontSize=11,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            fontSize=14,
            textColor=PRIMARY_COLOR,
            spaceBefore=16,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        )
    )
    return styles


def _student_info_table(student_info: Dict) -> Table:
    """Build a two-column table of student details."""
    data = [
        ["Name", student_info.get("name", "-")],
        ["University", student_info.get("university", "-")],
        ["Branch", student_info.get("branch", "-")],
        ["Admission Year", str(student_info.get("year", "-"))],
    ]
    table = Table(data, colWidths=[5 * cm, 9 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRID),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ]
        )
    )
    return table


def _semester_table(semester_summary: List[Dict]) -> Table:
    """Build the semester-wise SGPA/credit/running-CGPA table."""
    header = ["Semester", "SGPA", "Credits", "Running CGPA"]
    data = [header]
    for row in semester_summary:
        data.append(
            [row["Semester"], row["SGPA"], row["Credits"], row["Running CGPA"]]
        )

    table = Table(data, colWidths=[3 * cm, 3.5 * cm, 3.5 * cm, 4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRID]),
            ]
        )
    )
    return table


def _metrics_table(metrics: List[List[str]]) -> Table:
    """Build a simple metric-label/value table (e.g. CGPA, Percentage)."""
    table = Table(metrics, colWidths=[6 * cm, 6 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRID),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (1, 0), (1, -1), PRIMARY_COLOR),
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ]
        )
    )
    return table


def generate_pdf_report(
    output_path: str,
    student_info: Dict,
    calculator_result: Dict,
    target_cgpa: Optional[float],
    planner_result: Optional[Dict],
    ai_result: Optional[Dict],
    sgpa_list: List[float],
    credit_list: List[float],
) -> str:
    """
    Assemble and write the full PDF academic report to disk.

    Args:
        output_path: Destination file path for the generated PDF.
        student_info: Dict with name, university, branch, year.
        calculator_result: Output of calculator.calculate_full_report().
        target_cgpa: The student's desired final CGPA (or None).
        planner_result: Output of planner.calculate_required_sgpa() (or None).
        ai_result: Output of advisor.get_ai_recommendation() (or None).
        sgpa_list: Chronological list of completed SGPAs (for charts).
        credit_list: Chronological list of completed credits (for charts).

    Returns:
        The output_path, for convenient chaining.
    """
    styles = _build_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )

    story = []

    # --- Title ---
    story.append(Paragraph("Smart CGPA Calculator & AI Academic Advisor", styles["ReportTitle"]))
    story.append(Paragraph("Personalized Academic Performance Report", styles["ReportSubtitle"]))

    # --- Student Info ---
    story.append(Paragraph("Student Information", styles["SectionHeading"]))
    story.append(_student_info_table(student_info))
    story.append(Spacer(1, 10))

    # --- Semester Table ---
    if calculator_result.get("semester_summary"):
        story.append(Paragraph("Semester-wise Record", styles["SectionHeading"]))
        story.append(_semester_table(calculator_result["semester_summary"]))
        story.append(Spacer(1, 10))

    # --- Current Standing ---
    story.append(Paragraph("Current Academic Standing", styles["SectionHeading"]))
    metrics = [
        ["Current CGPA", f"{calculator_result.get('cgpa', 0):.2f}"],
        ["Percentage", f"{calculator_result.get('percentage', 0):.2f}%"],
        ["Completed Credits", f"{calculator_result.get('total_credits', 0):.1f}"],
    ]
    story.append(_metrics_table(metrics))
    story.append(Spacer(1, 10))

    # --- Target Planner ---
    if target_cgpa is not None and planner_result is not None:
        story.append(Paragraph("Target CGPA Planning", styles["SectionHeading"]))
        planner_metrics = [
            ["Target CGPA", f"{target_cgpa:.2f}"],
            [
                "Required Future SGPA",
                f"{planner_result.get('required_sgpa', '-')}"
                if planner_result.get("required_sgpa") is not None
                else "-",
            ],
            ["Achievable", "Yes" if planner_result.get("achievable") else "No"],
        ]
        story.append(_metrics_table(planner_metrics))
        story.append(Spacer(1, 6))
        story.append(Paragraph(planner_result.get("message", ""), styles["BodyText"]))
        story.append(Spacer(1, 10))

    # --- AI Recommendations ---
    if ai_result is not None:
        story.append(Paragraph("AI Academic Advisor Recommendations", styles["SectionHeading"]))
        ai_metrics = [
            ["Performance Level", ai_result.get("performance_level", "-")],
            ["Trend", ai_result.get("trend", "-")],
            ["Chance of Achieving Target", ai_result.get("chance_label", "-")],
        ]
        story.append(_metrics_table(ai_metrics))
        story.append(Spacer(1, 8))

        suggestions = ai_result.get("suggestions", [])
        if suggestions:
            story.append(Paragraph("Study Suggestions:", styles["BodyText"]))
            items = [ListItem(Paragraph(s, styles["BodyText"])) for s in suggestions]
            story.append(ListFlowable(items, bulletType="bullet", start="circle"))
        story.append(Spacer(1, 10))

    # --- Charts ---
    story.append(Paragraph("Performance Charts", styles["SectionHeading"]))

    with tempfile.TemporaryDirectory() as tmp_dir:
        chart_paths = []
        if sgpa_list:
            trend_fig = graphs.plot_sgpa_trend(sgpa_list)
            trend_path = os.path.join(tmp_dir, "trend.png")
            graphs.save_figure(trend_fig, trend_path)
            chart_paths.append(trend_path)

            perf_fig = graphs.plot_semester_performance(sgpa_list)
            perf_path = os.path.join(tmp_dir, "performance.png")
            graphs.save_figure(perf_fig, perf_path)
            chart_paths.append(perf_path)

        if credit_list:
            credit_fig = graphs.plot_credit_distribution(credit_list)
            credit_path = os.path.join(tmp_dir, "credits.png")
            graphs.save_figure(credit_fig, credit_path)
            chart_paths.append(credit_path)

        if not chart_paths:
            story.append(Paragraph("No chart data available yet.", styles["BodyText"]))
        else:
            for path in chart_paths:
                story.append(Image(path, width=16 * cm, height=16 * cm * 3.5 / 6))
                story.append(Spacer(1, 8))

        doc.build(story)

    return output_path
