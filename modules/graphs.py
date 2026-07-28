"""
graphs.py
---------
Matplotlib chart-generation utilities for the dashboard and PDF report.

Each function returns a matplotlib Figure object so callers (Streamlit
UI or the PDF generator) can decide how to render/save it, keeping
this module free of any Streamlit or ReportLab specific code.
"""

from typing import List
import matplotlib
matplotlib.use("Agg")  # safe for headless/server rendering
import matplotlib.pyplot as plt


# A calm, professional color palette used consistently across charts
PRIMARY_COLOR = "#2E5EAA"
SECONDARY_COLOR = "#4CAF50"
ACCENT_COLOR = "#FF9800"
GRID_COLOR = "#DDDDDD"


def _style_axes(ax):
    """Apply a shared, clean visual style to a matplotlib Axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
    ax.set_axisbelow(True)


def plot_sgpa_trend(sgpa_list: List[float]):
    """
    Line chart showing SGPA progression across completed semesters.

    Args:
        sgpa_list: Chronological list of completed SGPAs.

    Returns:
        A matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)

    if not sgpa_list:
        ax.text(0.5, 0.5, "No semester data available", ha="center", va="center")
        ax.axis("off")
        return fig

    semesters = list(range(1, len(sgpa_list) + 1))
    ax.plot(
        semesters, sgpa_list, marker="o", color=PRIMARY_COLOR,
        linewidth=2, markersize=6, markerfacecolor="white",
        markeredgewidth=2, markeredgecolor=PRIMARY_COLOR,
    )
    ax.fill_between(semesters, sgpa_list, min(sgpa_list) - 0.5 if sgpa_list else 0,
                     color=PRIMARY_COLOR, alpha=0.08)

    ax.set_title("SGPA Trend Across Semesters", fontsize=12, fontweight="bold")
    ax.set_xlabel("Semester")
    ax.set_ylabel("SGPA")
    ax.set_xticks(semesters)
    ax.set_ylim(0, 10)
    _style_axes(ax)
    fig.tight_layout()
    return fig


def plot_semester_performance(sgpa_list: List[float]):
    """
    Bar chart comparing SGPA per semester against the overall average.

    Args:
        sgpa_list: Chronological list of completed SGPAs.

    Returns:
        A matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)

    if not sgpa_list:
        ax.text(0.5, 0.5, "No semester data available", ha="center", va="center")
        ax.axis("off")
        return fig

    semesters = [f"Sem {i}" for i in range(1, len(sgpa_list) + 1)]
    avg = sum(sgpa_list) / len(sgpa_list)

    colors = [SECONDARY_COLOR if s >= avg else ACCENT_COLOR for s in sgpa_list]
    ax.bar(semesters, sgpa_list, color=colors, width=0.55, zorder=3)
    ax.axhline(avg, color=PRIMARY_COLOR, linestyle="--", linewidth=1.5,
                label=f"Average ({avg:.2f})")

    ax.set_title("Semester-wise Performance", fontsize=12, fontweight="bold")
    ax.set_ylabel("SGPA")
    ax.set_ylim(0, 10)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    _style_axes(ax)
    fig.tight_layout()
    return fig


def plot_credit_distribution(credit_list: List[float]):
    """
    Pie chart showing how completed credits are distributed across
    semesters.

    Args:
        credit_list: Chronological list of completed credits.

    Returns:
        A matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)

    if not credit_list:
        ax.text(0.5, 0.5, "No credit data available", ha="center", va="center")
        ax.axis("off")
        return fig

    labels = [f"Sem {i}" for i in range(1, len(credit_list) + 1)]
    palette = plt.cm.Blues(
        [0.9 - (0.5 * i / max(len(credit_list) - 1, 1)) for i in range(len(credit_list))]
    )

    ax.pie(
        credit_list,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        colors=palette,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 8},
    )
    ax.set_title("Credit Distribution by Semester", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


def save_figure(fig, path: str) -> str:
    """
    Persist a matplotlib figure to disk as a PNG (used by the PDF
    generator, which needs image files rather than live figures).

    Args:
        fig: The matplotlib Figure to save.
        path: Destination file path (should end in .png).

    Returns:
        The same path, for convenient chaining.
    """
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return path
