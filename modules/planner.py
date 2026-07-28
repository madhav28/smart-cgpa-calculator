"""
planner.py
----------
Target CGPA planning logic.

This module answers the question: "Given my completed SGPAs/credits
and how many credits remain, what SGPA do I need in the remaining
semesters to hit my target final CGPA?"

This is PURE MATHEMATICS (no Machine Learning), derived directly from
the weighted-average CGPA formula:

    Target_CGPA = (Sum(completed_SGPA * completed_credit) + Required_SGPA * remaining_credit)
                  / (Sum(completed_credit) + remaining_credit)

Solving for Required_SGPA:

    Required_SGPA = (Target_CGPA * Total_Credits - Sum(completed_SGPA * completed_credit))
                    / remaining_credit
"""

from typing import List, Dict
import numpy as np

from modules.calculator import calculate_cgpa


MAX_SGPA = 10.0
MIN_SGPA = 0.0


def calculate_required_sgpa(
    completed_sgpas: List[float],
    completed_credits: List[float],
    remaining_credits: float,
    target_cgpa: float,
) -> Dict:
    """
    Calculate the exact SGPA required in the remaining semesters to
    reach a target final CGPA.

    Args:
        completed_sgpas: SGPAs of semesters already completed.
        completed_credits: Credits of semesters already completed.
        remaining_credits: Total credits left in remaining semesters.
        target_cgpa: The final CGPA the student wants to achieve.

    Returns:
        Dictionary containing:
            - required_sgpa: The exact SGPA needed (unclamped, may be
              outside 0-10 to show feasibility).
            - achievable: Whether required_sgpa falls within [0, 10].
            - message: A human readable explanation.
    """
    if remaining_credits is None or remaining_credits <= 0:
        return {
            "required_sgpa": None,
            "achievable": False,
            "message": "No remaining credits to plan for. "
                       "Please enter the credits for your upcoming semesters.",
        }

    completed_weighted_sum = float(
        np.sum(np.array(completed_sgpas, dtype=float) * np.array(completed_credits, dtype=float))
    ) if completed_sgpas and completed_credits else 0.0

    completed_credit_total = float(np.sum(completed_credits)) if completed_credits else 0.0
    total_credits = completed_credit_total + remaining_credits

    required_sgpa = (
        (target_cgpa * total_credits) - completed_weighted_sum
    ) / remaining_credits

    required_sgpa_rounded = round(required_sgpa, 2)
    achievable = MIN_SGPA <= required_sgpa_rounded <= MAX_SGPA

    if required_sgpa_rounded > MAX_SGPA:
        message = (
            f"Target not achievable: you would need an SGPA of "
            f"{required_sgpa_rounded}, which exceeds the maximum possible "
            f"({MAX_SGPA})."
        )
    elif required_sgpa_rounded < MIN_SGPA:
        message = (
            "Target is already guaranteed based on your current CGPA — "
            "you can score as low as 0 and still meet it (not recommended!)."
        )
    else:
        message = (
            f"You need an average SGPA of {required_sgpa_rounded} in your "
            f"remaining semesters to reach a CGPA of {target_cgpa}."
        )

    return {
        "required_sgpa": required_sgpa_rounded,
        "achievable": achievable,
        "message": message,
    }


def simulate_target_scenarios(
    completed_sgpas: List[float],
    completed_credits: List[float],
    remaining_credits: float,
    target_cgpas: List[float],
) -> List[Dict]:
    """
    Run the required-SGPA calculation for several target CGPA values
    at once, useful for showing a "what-if" table in the dashboard.

    Args:
        completed_sgpas: SGPAs of semesters already completed.
        completed_credits: Credits of semesters already completed.
        remaining_credits: Total credits left in remaining semesters.
        target_cgpas: A list of candidate target CGPA values.

    Returns:
        List of dictionaries, one per target, each containing the
        target value and the corresponding required SGPA result.
    """
    scenarios = []
    for target in target_cgpas:
        result = calculate_required_sgpa(
            completed_sgpas, completed_credits, remaining_credits, target
        )
        scenarios.append({"target_cgpa": target, **result})
    return scenarios


def current_cgpa_from_completed(
    completed_sgpas: List[float], completed_credits: List[float]
) -> float:
    """
    Small convenience wrapper around calculate_cgpa so the planner
    module doesn't force the UI to import calculator directly for
    this specific use case.

    Args:
        completed_sgpas: SGPAs of semesters already completed.
        completed_credits: Credits of semesters already completed.

    Returns:
        The current CGPA based on completed semesters only.
    """
    return calculate_cgpa(completed_sgpas, completed_credits)
