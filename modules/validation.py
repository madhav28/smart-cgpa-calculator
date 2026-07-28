"""
validation.py
--------------
Centralized input validation utilities for the Smart CGPA Calculator.

All validation logic lives here so that other modules (calculator,
planner, advisor, app) can simply call these helpers instead of
duplicating checks. Keeping validation isolated also makes it easy
to unit test independently of the Streamlit UI.
"""

from typing import List, Tuple, Optional


MIN_SGPA = 0.0
MAX_SGPA = 10.0
MIN_CREDITS = 0.0


def is_valid_sgpa(sgpa: Optional[float]) -> bool:
    """
    Check whether a single SGPA value is within the allowed range.

    Args:
        sgpa: The SGPA value to validate (can be None for empty input).

    Returns:
        True if the SGPA is a number between MIN_SGPA and MAX_SGPA
        (inclusive), False otherwise.
    """
    if sgpa is None:
        return False
    try:
        value = float(sgpa)
    except (TypeError, ValueError):
        return False
    return MIN_SGPA <= value <= MAX_SGPA


def is_valid_credit(credit: Optional[float]) -> bool:
    """
    Check whether a credit value is a positive number.

    Args:
        credit: The credit value to validate (can be None for empty input).

    Returns:
        True if the credit is a positive number, False otherwise.
    """
    if credit is None:
        return False
    try:
        value = float(credit)
    except (TypeError, ValueError):
        return False
    return value > MIN_CREDITS


def is_semester_filled(sgpa: Optional[float], credit: Optional[float]) -> bool:
    """
    Determine whether a semester row has actually been filled in by
    the user (i.e. is not an empty/skipped semester row).

    A semester is considered "filled" only if BOTH sgpa and credit
    contain some non-empty value. This allows the UI to safely ignore
    rows where a student has not yet completed that semester.

    Args:
        sgpa: Raw SGPA input (may be None, empty string, or a number).
        credit: Raw credit input (may be None, empty string, or a number).

    Returns:
        True if both fields contain a non-empty value, else False.
    """
    def _has_value(x):
        if x is None:
            return False
        if isinstance(x, str) and x.strip() == "":
            return False
        return True

    return _has_value(sgpa) and _has_value(credit)


def validate_semesters(
    sgpa_list: List[Optional[float]],
    credit_list: List[Optional[float]],
) -> Tuple[List[float], List[float], List[str]]:
    """
    Validate a full list of semester SGPA/credit pairs.

    Empty semesters (where both fields are blank) are silently
    ignored/skipped as per the project requirement. Semesters with
    partially filled or out-of-range data produce an error message.

    Args:
        sgpa_list: List of SGPA inputs, one per semester slot.
        credit_list: List of credit inputs, one per semester slot.

    Returns:
        A tuple of (clean_sgpas, clean_credits, error_messages) where
        clean_sgpas/clean_credits only contain validated, completed
        semesters, and error_messages contains a human readable
        message for each row that failed validation.
    """
    clean_sgpas: List[float] = []
    clean_credits: List[float] = []
    errors: List[str] = []

    for idx, (sgpa, credit) in enumerate(zip(sgpa_list, credit_list), start=1):
        # Skip fully empty semesters (student hasn't studied that far yet)
        if not is_semester_filled(sgpa, credit):
            continue

        row_errors = []
        if not is_valid_sgpa(sgpa):
            row_errors.append(f"SGPA must be between {MIN_SGPA} and {MAX_SGPA}")
        if not is_valid_credit(credit):
            row_errors.append("Credits must be a positive number")

        if row_errors:
            errors.append(f"Semester {idx}: " + "; ".join(row_errors))
        else:
            clean_sgpas.append(float(sgpa))
            clean_credits.append(float(credit))

    return clean_sgpas, clean_credits, errors


def validate_target_cgpa(target: Optional[float]) -> Tuple[bool, str]:
    """
    Validate a target CGPA entered by the student for future planning.

    Args:
        target: The desired final CGPA.

    Returns:
        Tuple of (is_valid, error_message). error_message is an empty
        string when is_valid is True.
    """
    if target is None:
        return False, "Target CGPA cannot be empty."
    try:
        value = float(target)
    except (TypeError, ValueError):
        return False, "Target CGPA must be a number."
    if not (MIN_SGPA <= value <= MAX_SGPA):
        return False, f"Target CGPA must be between {MIN_SGPA} and {MAX_SGPA}."
    return True, ""


def validate_student_info(name: str, university: str, branch: str, year: Optional[int]) -> List[str]:
    """
    Validate basic student information fields.

    Args:
        name: Student's full name.
        university: University/college name.
        branch: Branch/department of study.
        year: Admission year.

    Returns:
        List of error messages (empty list means everything is valid).
    """
    errors = []
    if not name or not name.strip():
        errors.append("Student name is required.")
    if not university or not university.strip():
        errors.append("University name is required.")
    if not branch or not branch.strip():
        errors.append("Branch is required.")
    if year is None:
        errors.append("Admission year is required.")
    else:
        try:
            year_val = int(year)
            if year_val < 1980 or year_val > 2100:
                errors.append("Admission year seems invalid.")
        except (TypeError, ValueError):
            errors.append("Admission year must be a valid number.")
    return errors
