"""
interactive_charts.py
----------------------
Plotly-based INTERACTIVE chart utilities for the live Streamlit
dashboard (hover tooltips, zoom/pan, smooth animations).

This is intentionally separate from graphs.py, which produces static
Matplotlib charts used only for the PDF export (ReportLab needs plain
PNG images, not interactive widgets). Keeping them apart avoids mixing
two charting backends inside one module.

All functions return a plotly.graph_objects.Figure ready to be passed
straight to st.plotly_chart().

THEMING: every function accepts an optional `colors` dict (see
DEFAULT_COLORS below) so the active app theme can recolor charts to
match. This affects ONLY visual color values — the data passed in,
the math performed, the traces plotted, and every number shown on the
charts are completely unchanged regardless of `colors`. Callers that
don't pass `colors` get the original default palette, so this is a
fully backward-compatible addition.
"""

from typing import List, Optional, Dict
import plotly.graph_objects as go

# Fallback palette used whenever a caller doesn't supply theme colors.
DEFAULT_COLORS: Dict[str, str] = {
    "primary": "#8B5CF6",
    "secondary": "#F472B6",
    "accent": "#22D3EE",
    "good": "#34D399",
    "warn": "#FBBF24",
    "bad": "#F87171",
    "grid": "rgba(255,255,255,0.08)",
    "text": "#E5E7EB",
}


def _resolve_colors(colors: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Merge a partial/complete color override on top of DEFAULT_COLORS."""
    resolved = dict(DEFAULT_COLORS)
    if colors:
        resolved.update({k: v for k, v in colors.items() if v})
    return resolved


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    Convert a '#RRGGBB' hex string to an 'rgba(r,g,b,a)' string. Falls
    back to a neutral gray if given something that isn't a plain hex
    color (e.g. an rgba(...) string was passed straight through).
    """
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return f"rgba(139,92,246,{alpha})"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _base_layout(c: Dict[str, str]) -> dict:
    """Shared Plotly layout options, using the resolved theme colors."""
    return dict(
        font=dict(family="Inter, sans-serif", size=13, color=c["text"]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor="#1F2029", font_size=13, font_family="Inter", font_color="#F4F4F6"),
    )


def sgpa_trend_chart(sgpa_list: List[float], colors: Optional[Dict[str, str]] = None):
    """
    Interactive line chart of SGPA across semesters with a smooth
    gradient-filled area and hover tooltips.
    """
    c = _resolve_colors(colors)
    base = _base_layout(c)
    fig = go.Figure()

    if not sgpa_list:
        fig.update_layout(**base, annotations=[
            dict(text="No semester data yet", showarrow=False, font=dict(size=14))
        ])
        return fig

    semesters = list(range(1, len(sgpa_list) + 1))
    fig.add_trace(
        go.Scatter(
            x=semesters,
            y=sgpa_list,
            mode="lines+markers",
            line=dict(color=c["primary"], width=3, shape="spline"),
            marker=dict(size=9, color="white", line=dict(color=c["primary"], width=2)),
            fill="tozeroy",
            fillcolor=_hex_to_rgba(c["primary"], 0.10),
            hovertemplate="Semester %{x}<br>SGPA: <b>%{y:.2f}</b><extra></extra>",
            name="SGPA",
        )
    )
    fig.update_layout(
        **base,
        title=dict(text="SGPA Trend Across Semesters", font=dict(size=15, family="Poppins")),
        xaxis=dict(title="Semester", tickmode="linear", gridcolor=c["grid"], zeroline=False),
        yaxis=dict(title="SGPA", range=[0, 10.3], gridcolor=c["grid"], zeroline=False),
        height=340,
        showlegend=False,
    )
    return fig


def semester_performance_chart(sgpa_list: List[float], colors: Optional[Dict[str, str]] = None):
    """
    Interactive bar chart comparing each semester's SGPA to the
    running average, with color-coded bars (above/below average).
    """
    c = _resolve_colors(colors)
    base = _base_layout(c)
    fig = go.Figure()

    if not sgpa_list:
        fig.update_layout(**base, annotations=[
            dict(text="No semester data yet", showarrow=False, font=dict(size=14))
        ])
        return fig

    labels = [f"Sem {i}" for i in range(1, len(sgpa_list) + 1)]
    avg = sum(sgpa_list) / len(sgpa_list)
    bar_colors = [c["good"] if s >= avg else c["warn"] for s in sgpa_list]

    fig.add_trace(
        go.Bar(
            x=labels,
            y=sgpa_list,
            marker=dict(color=bar_colors, line=dict(width=0)),
            hovertemplate="%{x}<br>SGPA: <b>%{y:.2f}</b><extra></extra>",
            name="SGPA",
        )
    )
    fig.add_hline(
        y=avg, line_dash="dash", line_color=c["primary"], line_width=2,
        annotation_text=f"Average {avg:.2f}", annotation_position="top left",
        annotation_font=dict(color=c["primary"], size=12),
    )
    fig.update_layout(
        **base,
        title=dict(text="Semester-wise Performance", font=dict(size=15, family="Poppins")),
        yaxis=dict(title="SGPA", range=[0, 10.3], gridcolor=c["grid"], zeroline=False),
        xaxis=dict(gridcolor=c["grid"]),
        height=340,
        showlegend=False,
    )
    return fig


def credit_distribution_chart(credit_list: List[float], colors: Optional[Dict[str, str]] = None):
    """Interactive donut chart of credit distribution across semesters."""
    c = _resolve_colors(colors)
    base = _base_layout(c)
    fig = go.Figure()

    if not credit_list:
        fig.update_layout(**base, annotations=[
            dict(text="No credit data yet", showarrow=False, font=dict(size=14))
        ])
        return fig

    labels = [f"Sem {i}" for i in range(1, len(credit_list) + 1)]
    wheel = [c["primary"], c["secondary"], c["accent"], c["good"], c["warn"]]
    wheel_colors = [wheel[i % len(wheel)] for i in range(len(credit_list))]

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=credit_list,
            hole=0.55,
            marker=dict(colors=wheel_colors, line=dict(color="white", width=2)),
            textinfo="percent",
            hovertemplate="%{label}<br>%{value} credits (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(
        **base,
        title=dict(text="Credit Distribution by Semester", font=dict(size=15, family="Poppins")),
        height=360,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        annotations=[dict(text=f"{int(sum(credit_list))}<br>credits", x=0.5, y=0.5,
                           font=dict(size=15, family="Poppins", color=c["text"]), showarrow=False)],
    )
    return fig


def cgpa_gauge(cgpa: float, target_cgpa: Optional[float] = None, colors: Optional[Dict[str, str]] = None):
    """
    Speedometer-style gauge showing current CGPA on a 0-10 scale,
    with color bands and an optional target-CGPA threshold marker.
    """
    c = _resolve_colors(colors)
    base = _base_layout(c)

    steps = [
        dict(range=[0, 5], color=_hex_to_rgba(c["bad"], 0.18)),
        dict(range=[5, 7], color=_hex_to_rgba(c["warn"], 0.18)),
        dict(range=[7, 8.5], color=_hex_to_rgba(c["accent"], 0.18)),
        dict(range=[8.5, 10], color=_hex_to_rgba(c["good"], 0.18)),
    ]
    threshold = dict(
        line=dict(color=c["secondary"], width=4),
        thickness=0.8,
        value=target_cgpa if target_cgpa is not None else cgpa,
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=cgpa,
            number=dict(suffix=" / 10", font=dict(size=32, family="Poppins", color=c["primary"])),
            gauge=dict(
                axis=dict(range=[0, 10], tickwidth=1, tickcolor="#6B7280", tickfont=dict(color=c["text"])),
                bar=dict(color=c["primary"], thickness=0.28),
                bgcolor="rgba(255,255,255,0.03)",
                borderwidth=0,
                steps=steps,
                threshold=threshold,
            ),
            domain=dict(x=[0, 1], y=[0, 1]),
        )
    )
    fig.update_layout(**base)
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10))
    return fig


def chance_gauge(chance_label: str, colors: Optional[Dict[str, str]] = None):
    """
    Compact gauge translating the AI Advisor's categorical
    High/Medium/Low prediction into a visual 0-100 confidence-style
    ring.
    """
    c = _resolve_colors(colors)
    base = _base_layout(c)

    mapping = {"Low": (20, c["bad"]), "Medium": (55, c["warn"]), "High": (88, c["good"])}
    value, color = mapping.get(chance_label, (50, c["warn"]))

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number=dict(suffix="%", font=dict(size=26, family="Poppins", color=color)),
            gauge=dict(
                axis=dict(range=[0, 100], visible=False),
                bar=dict(color=color, thickness=0.3),
                bgcolor="rgba(255,255,255,0.04)",
                borderwidth=0,
            ),
        )
    )
    fig.update_layout(**base)
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
    return fig


def advisor_radar(
    avg_sgpa: float,
    consistency_std: float,
    trend_slope: float,
    chance_label: str,
    colors: Optional[Dict[str, str]] = None,
):
    """
    Radar/spider chart summarizing the AI Advisor's four analysis
    dimensions on a common 0-10 scale so a student can see their
    overall academic "shape" at a glance.

    Args:
        avg_sgpa: Average SGPA across completed semesters.
        consistency_std: Standard deviation of SGPAs (lower = better);
            converted here into a 0-10 "Consistency" score.
        trend_slope: Linear-fit slope of SGPA over semesters; mapped
            into a 0-10 "Momentum" score centered at 5.
        chance_label: High/Medium/Low chance-of-success label, mapped
            to a 0-10 "Target Readiness" score.
        colors: Optional theme color overrides (visual only).
    """
    c = _resolve_colors(colors)
    base = _base_layout(c)

    consistency_score = max(0.0, min(10.0, 10 - consistency_std * 6))
    momentum_score = max(0.0, min(10.0, 5 + trend_slope * 8))
    chance_map = {"Low": 3.0, "Medium": 6.0, "High": 9.0}
    readiness_score = chance_map.get(chance_label, 5.0)
    performance_score = max(0.0, min(10.0, avg_sgpa))

    categories = ["Performance", "Consistency", "Momentum", "Target Readiness"]
    values = [performance_score, consistency_score, momentum_score, readiness_score]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + values[:1],
            theta=categories + categories[:1],
            fill="toself",
            fillcolor=_hex_to_rgba(c["primary"], 0.25),
            line=dict(color=c["primary"], width=2),
            hovertemplate="%{theta}: <b>%{r:.1f}</b>/10<extra></extra>",
        )
    )
    fig.update_layout(
        **base,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor=c["grid"]),
            angularaxis=dict(gridcolor=c["grid"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=340,
        showlegend=False,
        title=dict(text="Academic Profile Radar", font=dict(size=15, family="Poppins")),
    )
    return fig


def what_if_curve(
    completed_sgpas: List[float],
    completed_credits: List[float],
    remaining_credits: float,
    colors: Optional[Dict[str, str]] = None,
):
    """
    Interactive curve showing required future SGPA across a sweep of
    possible target CGPAs (5.0 to 10.0), so a student can visually
    explore the trade-off before committing to a target.
    """
    from modules import planner  # local import avoids a circular dependency at module load time

    c = _resolve_colors(colors)
    base = _base_layout(c)
    fig = go.Figure()

    if not completed_sgpas or not remaining_credits or remaining_credits <= 0:
        fig.update_layout(**base, height=320, annotations=[
            dict(text="Enter remaining credits to see this chart", showarrow=False, font=dict(size=13))
        ])
        return fig

    targets = [round(5.0 + 0.1 * i, 2) for i in range(51)]
    required = []
    for t in targets:
        result = planner.calculate_required_sgpa(
            completed_sgpas, completed_credits, remaining_credits, t
        )
        required.append(result["required_sgpa"])

    valid_required = [r for r in required if r is not None]

    fig.add_trace(
        go.Scatter(
            x=targets, y=required, mode="lines",
            line=dict(color=c["primary"], width=3, shape="spline"),
            hovertemplate="Target CGPA %{x:.1f}<br>Required SGPA: <b>%{y:.2f}</b><extra></extra>",
        )
    )
    if valid_required:
        upper_bound = max(max(valid_required), 10)
        fig.add_hrect(y0=10, y1=upper_bound, fillcolor=c["bad"], opacity=0.06, line_width=0)
    fig.add_hline(y=10, line_dash="dot", line_color=c["bad"], annotation_text="Max possible SGPA",
                  annotation_font=dict(size=11, color=c["bad"]))
    fig.update_layout(
        **base,
        title=dict(text="What If: Required SGPA vs Target CGPA", font=dict(size=15, family="Poppins")),
        xaxis=dict(title="Target CGPA", gridcolor=c["grid"]),
        yaxis=dict(title="Required Future SGPA", gridcolor=c["grid"]),
        height=320,
    )
    return fig
