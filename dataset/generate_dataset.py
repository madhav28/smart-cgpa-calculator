"""
generate_dataset.py
--------------------
One-off utility script used to generate the synthetic historical
dataset (student_dataset.csv) that models/train_model.py trains on.

This is NOT part of the runtime application — it is kept here purely
for transparency/reproducibility so anyone can see how the training
data was produced and regenerate it if needed.

The synthetic data simulates realistic university student academic
records with a mix of improving, declining, and stable performers so
the AI Advisor model can learn meaningful patterns for:
    - performance_level (Excellent / Good / Average / Below Average)
    - chance_label (High / Medium / Low chance of hitting their target)
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N_STUDENTS = 1200


def classify_performance(avg_sgpa: float) -> str:
    """Rule-based ground truth label for overall performance level."""
    if avg_sgpa >= 8.5:
        return "Excellent"
    elif avg_sgpa >= 7.0:
        return "Good"
    elif avg_sgpa >= 5.5:
        return "Average"
    else:
        return "Below Average"


def classify_chance(required_sgpa: float, avg_sgpa: float, trend_slope: float, sgpa_std: float) -> str:
    """
    Rule-based ground truth label for chance of achieving the target,
    factoring in the gap between required SGPA and current average,
    the student's trend (improving/declining) and consistency.
    """
    gap = required_sgpa - avg_sgpa
    stability_bonus = -sgpa_std * 0.5
    trend_bonus = trend_slope * 2
    score = -gap + trend_bonus + stability_bonus

    if required_sgpa > 10:
        return "Low"
    if score >= 0.5:
        return "High"
    elif score >= -1.0:
        return "Medium"
    else:
        return "Low"


rows = []
for sid in range(1, N_STUDENTS + 1):
    n_completed = np.random.randint(2, 7)  # 2 to 6 completed semesters

    base = np.random.uniform(4.5, 9.5)
    trend_type = np.random.choice(["improving", "declining", "stable"], p=[0.4, 0.25, 0.35])

    sgpas = []
    for sem in range(n_completed):
        if trend_type == "improving":
            drift = sem * np.random.uniform(0.05, 0.35)
        elif trend_type == "declining":
            drift = -sem * np.random.uniform(0.05, 0.35)
        else:
            drift = 0
        noise = np.random.normal(0, 0.35)
        sgpa = np.clip(base + drift + noise, 0, 10)
        sgpas.append(round(sgpa, 2))

    credits = list(np.random.choice([18, 20, 22, 24, 26], size=n_completed))
    completed_credits = float(np.sum(credits))

    avg_sgpa = float(np.average(sgpas, weights=credits))
    sgpa_std = float(np.std(sgpas))

    x = np.arange(n_completed)
    if n_completed > 1:
        trend_slope = float(np.polyfit(x, sgpas, 1)[0])
    else:
        trend_slope = 0.0

    remaining_semesters = np.random.randint(1, 6)
    remaining_credits = float(np.sum(np.random.choice([18, 20, 22, 24, 26], size=remaining_semesters)))

    target_cgpa = round(np.random.uniform(max(5.0, avg_sgpa - 1), min(10.0, avg_sgpa + 2)), 2)

    total_credits = completed_credits + remaining_credits
    completed_weighted = avg_sgpa * completed_credits
    required_sgpa = round(
        (target_cgpa * total_credits - completed_weighted) / remaining_credits, 2
    )

    performance_level = classify_performance(avg_sgpa)
    chance_label = classify_chance(required_sgpa, avg_sgpa, trend_slope, sgpa_std)

    rows.append(
        {
            "student_id": sid,
            "avg_sgpa": round(avg_sgpa, 2),
            "sgpa_std": round(sgpa_std, 2),
            "trend_slope": round(trend_slope, 3),
            "completed_credits": completed_credits,
            "remaining_credits": remaining_credits,
            "target_cgpa": target_cgpa,
            "required_sgpa": required_sgpa,
            "performance_level": performance_level,
            "chance_label": chance_label,
        }
    )

df = pd.DataFrame(rows)
df.to_csv("student_dataset.csv", index=False)
print(f"Generated {len(df)} rows -> student_dataset.csv")
print(df["performance_level"].value_counts())
print(df["chance_label"].value_counts())
