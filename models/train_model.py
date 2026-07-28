"""
train_model.py
---------------
Trains the AI Academic Advisor's Machine Learning models on the
historical dataset (dataset/student_dataset.csv) and saves them to
models/advisor_model.pkl using joblib.

IMPORTANT: ML is used ONLY for recommendation / academic-trend
analysis, never for the actual CGPA arithmetic (see modules/calculator.py
and modules/planner.py for the pure-math calculations).

Two classifiers are trained, sharing the same feature set:
    1. performance_clf -> predicts performance_level
       (Excellent / Good / Average / Below Average)
    2. chance_clf      -> predicts chance_label
       (High / Medium / Low chance of reaching the target CGPA)

Run this script directly to (re)train the model:
    python models/train_model.py
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

FEATURE_COLUMNS = [
    "avg_sgpa",
    "sgpa_std",
    "trend_slope",
    "completed_credits",
    "remaining_credits",
    "target_cgpa",
    "required_sgpa",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "student_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "advisor_model.pkl")


def load_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    """Load the historical student dataset from disk."""
    return pd.read_csv(path)


def train_and_save_models(df: pd.DataFrame, model_path: str = MODEL_PATH) -> dict:
    """
    Train both classifiers on the given dataframe and persist them
    (plus label encoders and feature column order) to a single
    joblib bundle.

    Args:
        df: Historical student dataset with feature + label columns.
        model_path: Destination path for the saved joblib bundle.

    Returns:
        Dictionary with training accuracy scores for both models.
    """
    X = df[FEATURE_COLUMNS]

    # --- Performance level classifier ---
    perf_encoder = LabelEncoder()
    y_perf = perf_encoder.fit_transform(df["performance_level"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_perf, test_size=0.2, random_state=42, stratify=y_perf
    )
    performance_clf = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42
    )
    performance_clf.fit(X_train, y_train)
    perf_acc = accuracy_score(y_test, performance_clf.predict(X_test))

    # --- Chance-of-success classifier ---
    chance_encoder = LabelEncoder()
    y_chance = chance_encoder.fit_transform(df["chance_label"])

    X_train2, X_test2, y_train2, y_test2 = train_test_split(
        X, y_chance, test_size=0.2, random_state=42, stratify=y_chance
    )
    chance_clf = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42
    )
    chance_clf.fit(X_train2, y_train2)
    chance_acc = accuracy_score(y_test2, chance_clf.predict(X_test2))

    bundle = {
        "performance_clf": performance_clf,
        "chance_clf": chance_clf,
        "performance_encoder": perf_encoder,
        "chance_encoder": chance_encoder,
        "feature_columns": FEATURE_COLUMNS,
    }
    joblib.dump(bundle, model_path)

    return {"performance_accuracy": perf_acc, "chance_accuracy": chance_acc}


def main():
    df = load_dataset()
    scores = train_and_save_models(df)
    print("Model training complete.")
    print(f"Performance-level accuracy : {scores['performance_accuracy']:.3f}")
    print(f"Chance-of-success accuracy  : {scores['chance_accuracy']:.3f}")
    print(f"Saved model bundle to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
