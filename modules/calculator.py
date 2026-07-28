"""
calculator.py
-------------
Pure mathematical CGPA/percentage calculation logic.

IMPORTANT: No Machine Learning is used anywhere in this module, per
project requirements. All calculations here are deterministic
weighted-average formulas.

Formulas used:
    CGPA       = Sum(SGPA_i * Credit_i) / Sum(Credit_i)
    Percentage = CGPA * 10
"""

from typing import List, Dict
import numpy as np


def calculate_cgpa(sgpa_list: List[float], credit_list: List[float]) -> float:
    """
    Calculate the weighted CGPA from a list of semester SGPAs and
    their corresponding credit loads.

    Args:
        sgpa_list: List of SGPA values for completed semesters.
        credit_list: List of credit totals for the same semesters.

    Returns:
        The weighted CGPA rounded to 2 decimal places. Returns 0.0
        if no valid semesters are provided.

    Raises:
        ValueError: If the two lists differ in length.
    """
    if len(sgpa_list) != len(credit_list):
        raise ValueError("sgpa_list and credit_list must be the same length")

    if not sgpa_list or not credit_list:
        return 0.0

    sgpa_arr = np.array(sgpa_list, dtype=float)
    credit_arr = np.array(credit_list, dtype=float)

    total_credits = credit_arr.sum()
    if total_credits <= 0:
        return 0.0

    weighted_sum = np.sum(sgpa_arr * credit_arr)
    cgpa = weighted_sum / total_credits
    return round(float(cgpa), 2)


def cgpa_to_percentage(cgpa: float) -> float:
    """
    Convert CGPA to an equivalent percentage using the standard
    university formula: Percentage = CGPA * 10.

    Args:
        cgpa: The CGPA value to convert.

    Returns:
        Percentage rounded to 2 decimal places.
    """
    return round(float(cgpa) * 10, 2)


def cgpa_to_percentage_ugc(cgpa: float) -> float:
    """
    Convert CGPA to percentage using the UGC-style formula common at
    many Indian universities: Percentage = (CGPA - 0.75) * 10.

    This is a SEPARATE, independent conversion from cgpa_to_percentage()
    (the "Direct 10x" formula) — neither formula is more "correct" than
    the other; different universities officially use different ones, so
    both are exposed for the UI to display side by side.

    Args:
        cgpa: The CGPA value to convert.

    Returns:
        Percentage rounded to 2 decimal places. Not clamped to 0-100:
        the raw formula result is always returned as-is (a very low
        CGPA can mathematically produce a negative value under this
        specific formula, which is expected behavior for the formula).
    """
    return round((float(cgpa) - 0.75) * 10, 2)


def total_completed_credits(credit_list: List[float]) -> float:
    """
    Sum up all completed credits.

    Args:
        credit_list: List of credit totals for completed semesters.

    Returns:
        Total credits completed so far.
    """
    if not credit_list:
        return 0.0
    return round(float(np.sum(np.array(credit_list, dtype=float))), 2)


def build_semester_summary(sgpa_list: List[float], credit_list: List[float]) -> List[Dict]:
    """
    Build a structured, per-semester summary table used for both the
    dashboard and the PDF report.

    Args:
        sgpa_list: List of validated SGPA values.
        credit_list: List of validated credit values.

    Returns:
        A list of dictionaries, each containing the semester number,
        SGPA, credits, and the running (cumulative) CGPA up to and
        including that semester.
    """
    summary = []
    running_weighted_sum = 0.0
    running_credits = 0.0

    for idx, (sgpa, credit) in enumerate(zip(sgpa_list, credit_list), start=1):
        running_weighted_sum += sgpa * credit
        running_credits += credit
        running_cgpa = (
            round(running_weighted_sum / running_credits, 2)
            if running_credits > 0
            else 0.0
        )
        summary.append(
            {
                "Semester": idx,
                "SGPA": round(sgpa, 2),
                "Credits": round(credit, 2),
                "Running CGPA": running_cgpa,
            }
        )
    return summary


def sgpa_to_grade(sgpa: float) -> str:
    """
    Convert a single SGPA/CGPA value into a common Indian university
    letter-grade label. Used purely for display (e.g. UI grade badges);
    has no effect on any calculation.

    Args:
        sgpa: The SGPA or CGPA value to convert.

    Returns:
        A short letter-grade string.
    """
    if sgpa >= 9.0:
        return "O"
    elif sgpa >= 8.0:
        return "A+"
    elif sgpa >= 7.0:
        return "A"
    elif sgpa >= 6.0:
        return "B+"
    elif sgpa >= 5.0:
        return "B"
    elif sgpa >= 4.0:
        return "C"
    else:
        return "F"


def calculate_full_report(sgpa_list: List[float], credit_list: List[float]) -> Dict:
    """
    Convenience wrapper that produces the complete set of calculator
    outputs needed by the dashboard in a single call.

    Args:
        sgpa_list: List of validated SGPA values.
        credit_list: List of validated credit values.

    Returns:
        Dictionary with cgpa, percentage (Direct 10x formula, unchanged
        for backward compatibility), percentage_ugc (the UGC formula,
        new), total_credits, and the per-semester summary table.
    """
    cgpa = calculate_cgpa(sgpa_list, credit_list)
    percentage = cgpa_to_percentage(cgpa)
    percentage_ugc = cgpa_to_percentage_ugc(cgpa)
    credits = total_completed_credits(credit_list)
    summary = build_semester_summary(sgpa_list, credit_list)

    return {
        "cgpa": cgpa,
        "percentage": percentage,
        "percentage_ugc": percentage_ugc,
        "total_credits": credits,
        "semester_summary": summary,
    }
