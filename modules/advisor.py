"""
advisor.py
----------
AI Academic Advisor.

This module is the ONLY place in the application that uses Machine
Learning. It loads the pre-trained classifiers from
models/advisor_model.pkl (trained by models/train_model.py) and uses
them purely for academic analysis / recommendations:

    - Performance level classification (Excellent/Good/Average/Below Average)
    - Chance of achieving the target CGPA (High/Medium/Low)

The academic "trend" and "consistency" features fed into the model
are computed with simple, transparent statistics (linear regression
slope and standard deviation) — this is standard feature engineering,
not a second ML model, and is kept separate from the CGPA arithmetic
in modules/calculator.py.
"""

import os
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "advisor_model.pkl")

_model_bundle = None  # lazy-loaded singleton


def _load_model():
    """Lazily load and cache the trained model bundle from disk."""
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "advisor_model.pkl not found. Please run "
                "'python models/train_model.py' first to train the model."
            )
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def compute_trend_slope(sgpa_list: List[float]) -> float:
    """
    Compute the academic trend as the slope of a best-fit line through
    the semester-wise SGPA values. Positive slope => improving trend,
    negative => declining, near-zero => stable.

    Args:
        sgpa_list: Chronological list of completed SGPAs.

    Returns:
        Slope of the linear fit (0.0 if fewer than 2 data points).
    """
    if len(sgpa_list) < 2:
        return 0.0
    x = np.arange(len(sgpa_list))
    slope = np.polyfit(x, sgpa_list, 1)[0]
    return round(float(slope), 3)


def compute_consistency(sgpa_list: List[float]) -> float:
    """
    Compute academic consistency as the standard deviation of SGPAs.
    A lower value means more consistent performance.

    Args:
        sgpa_list: Chronological list of completed SGPAs.

    Returns:
        Standard deviation of the SGPA list (0.0 if empty).
    """
    if not sgpa_list:
        return 0.0
    return round(float(np.std(sgpa_list)), 3)


def trend_label(slope: float) -> str:
    """Convert a numeric trend slope into a human-readable label."""
    if slope > 0.15:
        return "Improving"
    elif slope < -0.15:
        return "Declining"
    else:
        return "Stable"


def build_features(
    avg_sgpa: float,
    sgpa_std: float,
    trend_slope: float,
    completed_credits: float,
    remaining_credits: float,
    target_cgpa: float,
    required_sgpa: float,
):
    """
    Assemble a single feature row (as a DataFrame with correctly
    named columns) in the exact column order the model was trained
    on. Using a DataFrame instead of a raw list avoids sklearn's
    "X does not have valid feature names" warning and keeps inference
    consistent with training.
    """
    bundle = _load_model()
    ordered_values = {
        "avg_sgpa": avg_sgpa,
        "sgpa_std": sgpa_std,
        "trend_slope": trend_slope,
        "completed_credits": completed_credits,
        "remaining_credits": remaining_credits,
        "target_cgpa": target_cgpa,
        "required_sgpa": required_sgpa,
    }
    row = {col: [ordered_values[col]] for col in bundle["feature_columns"]}
    return pd.DataFrame(row)


def generate_study_suggestions(
    performance_level: str, chance_label: str, trend: str, required_sgpa: Optional[float]
) -> List[str]:
    """
    Rule-based (non-ML) study suggestions generated from the model's
    predictions. Keeping this rule-based keeps recommendations
    explainable and easy to maintain.

    Args:
        performance_level: Predicted performance level label.
        chance_label: Predicted chance-of-success label.
        trend: Human-readable trend label (Improving/Declining/Stable).
        required_sgpa: The SGPA required to hit the student's target.

    Returns:
        List of actionable suggestion strings.
    """
    suggestions = []

    if performance_level == "Excellent":
        suggestions.append("Maintain your current study routine — it's clearly working well.")
    elif performance_level == "Good":
        suggestions.append("Solid performance. Focus on your weaker subjects to push into the 'Excellent' range.")
    elif performance_level == "Average":
        suggestions.append("Consider a structured study schedule and regular revision to lift your average.")
    else:
        suggestions.append("Prioritize foundational concepts and seek mentorship or tutoring support.")

    if trend == "Declining":
        suggestions.append("Your SGPA trend is declining — review recent semesters to identify what changed.")
    elif trend == "Improving":
        suggestions.append("Great upward trend — keep reinforcing the habits driving this improvement.")
    else:
        suggestions.append("Your performance is stable — introduce small, incremental study goals to grow further.")

    if required_sgpa is not None:
        if required_sgpa > 10:
            suggestions.append(
                "Your target CGPA is mathematically out of reach with the remaining credits — "
                "consider revising your target or increasing remaining credits."
            )
        elif required_sgpa > 9:
            suggestions.append(
                "You'll need near-perfect SGPAs ahead — dedicate extra hours to high-credit subjects."
            )
        elif required_sgpa < 5:
            suggestions.append(
                "Your target is comfortably achievable — maintain consistent effort each semester."
            )

    if chance_label == "Low":
        suggestions.append("Chance of hitting your target is currently low — consider a more realistic interim goal.")
    elif chance_label == "Medium":
        suggestions.append("You're on the edge — a focused final push each semester can tip this in your favor.")
    else:
        suggestions.append("You're well-positioned to achieve your target — stay consistent.")

    return suggestions


def get_ai_recommendation(
    sgpa_list: List[float],
    completed_credits: float,
    remaining_credits: float,
    target_cgpa: float,
    required_sgpa: Optional[float],
) -> Dict:
    """
    Run the full AI Academic Advisor pipeline: feature engineering,
    ML inference, and rule-based suggestion generation.

    Args:
        sgpa_list: Chronological list of completed SGPAs.
        completed_credits: Total credits completed so far.
        remaining_credits: Total credits remaining.
        target_cgpa: Student's desired final CGPA.
        required_sgpa: Required SGPA computed by planner.py (may be
            None if remaining credits are unavailable).

    Returns:
        Dictionary with performance_level, chance_label, trend label,
        consistency score, and a list of study suggestions.
    """
    bundle = _load_model()

    avg_sgpa = float(np.average(sgpa_list)) if sgpa_list else 0.0
    sgpa_std = compute_consistency(sgpa_list)
    slope = compute_trend_slope(sgpa_list)
    trend = trend_label(slope)

    safe_required_sgpa = required_sgpa if required_sgpa is not None else avg_sgpa

    features = build_features(
        avg_sgpa=avg_sgpa,
        sgpa_std=sgpa_std,
        trend_slope=slope,
        completed_credits=completed_credits,
        remaining_credits=remaining_credits if remaining_credits else 0.0,
        target_cgpa=target_cgpa if target_cgpa is not None else avg_sgpa,
        required_sgpa=safe_required_sgpa,
    )

    perf_pred = bundle["performance_clf"].predict(features)[0]
    performance_level = bundle["performance_encoder"].inverse_transform([perf_pred])[0]

    chance_pred = bundle["chance_clf"].predict(features)[0]
    chance_label = bundle["chance_encoder"].inverse_transform([chance_pred])[0]

    suggestions = generate_study_suggestions(
        performance_level, chance_label, trend, required_sgpa
    )

    return {
        "performance_level": performance_level,
        "chance_label": chance_label,
        "trend": trend,
        "trend_slope": slope,
        "consistency_std": sgpa_std,
        "suggestions": suggestions,
    }
