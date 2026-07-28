"""
app.py
------
Smart CGPA Calculator & AI Academic Advisor
Main Streamlit application entry point.

This file is intentionally kept as a thin UI layer — all calculation,
validation, ML inference, chart, and PDF logic lives in the
`modules/` package. This keeps the UI and business logic cleanly
separated, per the project's coding standards.

UI/UX notes:
    - Glassmorphic cards, gradient hero banner, pill badges (styling.py)
    - Toggle-based semester entry with instant grade-pill feedback
    - CSV bulk-import for semester data, previewed/editable via st.data_editor
    - Contextual st.popover glossary tooltips (What is SGPA/CGPA?)
    - Live "what-if" target-planning chart that updates as you type,
      with no need to click Calculate first
    - st.status() step-by-step processing feed on Calculate
    - Interactive Plotly gauges/radar/donut charts (hover, zoom)
    - st.feedback thumbs rating on the AI Advisor's suggestions
    - Toast + confetti micro-interactions on success
    - 7-theme picker (Aurora/Ocean/Emerald/Sunset/Midnight/Light Academic/Auto),
      each with its own animated background, instantly swappable with no restart

Run with:
    streamlit run app.py
"""

import os
import tempfile

import pandas as pd
import streamlit as st

from modules import validation
from modules import calculator
from modules import planner
from modules import advisor
from modules import interactive_charts as ic
from modules import pdf_generator
from modules import styling


# --------------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart CGPA Calculator & AI Academic Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAX_SEMESTERS = 10
DEFAULT_SGPA = 7.5
DEFAULT_CREDITS = 20.0

DEMO_SGPAS = [8.6, 7.8, 9.0, 8.2, 7.5, 8.9, 8.1, 9.2, 7.9, 8.4]
DEMO_CREDITS = [24, 22, 24, 22, 24, 22, 24, 22, 24, 22]


# --------------------------------------------------------------------------
# Session state initialization
# --------------------------------------------------------------------------
def init_session_state():
    """Initialize all session-state keys used across reruns."""
    defaults = {
        "num_semesters": 6,
        "palette": "Aurora",
        "results_ready": False,
        "clean_sgpas": [],
        "clean_credits": [],
        "calc_result": None,
        "planner_result": None,
        "ai_result": None,
        "target_cgpa": None,
        "remaining_credits": 0.0,
        "prev_cgpa": None,
        "student_info": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()
styling.inject_custom_css(st.session_state["palette"])


# --------------------------------------------------------------------------
# Helpers: demo-fill / reset callbacks (must mutate session_state BEFORE
# the corresponding widgets are instantiated, so we do it via callbacks
# triggered on click, then Streamlit reruns and widgets pick up the
# fresh session_state values).
# --------------------------------------------------------------------------
def fill_demo_data():
    n = st.session_state["num_semesters"]
    for i in range(n):
        st.session_state[f"toggle_{i}"] = True
        st.session_state[f"sgpa_{i}"] = DEMO_SGPAS[i % len(DEMO_SGPAS)]
        st.session_state[f"credit_{i}"] = float(DEMO_CREDITS[i % len(DEMO_CREDITS)])
    st.session_state["target_cgpa_input"] = "9.0"
    st.session_state["remaining_credits_input"] = "40"
    st.toast("✨ Demo data loaded — hit Calculate!", icon="✨")


def reset_all():
    n = st.session_state["num_semesters"]
    for i in range(n):
        st.session_state[f"toggle_{i}"] = False
        st.session_state[f"sgpa_{i}"] = DEFAULT_SGPA
        st.session_state[f"credit_{i}"] = DEFAULT_CREDITS
    st.session_state["target_cgpa_input"] = ""
    st.session_state["remaining_credits_input"] = ""
    st.session_state["results_ready"] = False
    st.toast("🔄 Cleared. Start fresh!", icon="🔄")


# --------------------------------------------------------------------------
# Sidebar: Student Information + Appearance + Profile progress
# --------------------------------------------------------------------------
def render_sidebar():
    """Render the sidebar with student info, appearance, and setup controls."""
    st.sidebar.markdown("### 🎨 Appearance")
    theme_display = {f"{styling.THEME_ICONS[name]} {name}": name for name in styling.THEME_NAMES}
    display_options = list(theme_display.keys())
    current_display = f"{styling.THEME_ICONS[st.session_state['palette']]} {st.session_state['palette']}"
    st.session_state.setdefault("palette_picker", current_display)
    selected_display = st.sidebar.selectbox(
        "Theme", options=display_options,
        label_visibility="collapsed", key="palette_picker",
        help="Switches instantly — no restart needed. 'Auto' follows your system's light/dark setting.",
    )
    selected_theme = theme_display[selected_display]
    if selected_theme != st.session_state["palette"]:
        st.session_state["palette"] = selected_theme
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎓 Student Information")
    name = st.sidebar.text_input("Full Name", placeholder="e.g. Aditi Sharma", help="Shown on your PDF report")
    university = st.sidebar.text_input("University", placeholder="e.g. IIT Delhi")
    branch = st.sidebar.text_input("Branch", placeholder="e.g. Computer Science")
    year = st.sidebar.number_input("Admission Year", min_value=1980, max_value=2100, value=2022, step=1)

    filled = sum(1 for v in [name, university, branch] if v and v.strip()) + 1  # year always has a value
    st.sidebar.progress(filled / 4, text=f"Profile {int(filled / 4 * 100)}% complete")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Setup")
    num_semesters = st.sidebar.slider(
        "Number of semesters in your program", min_value=1, max_value=MAX_SEMESTERS,
        value=st.session_state["num_semesters"], help="Drag to match your program's total semester count",
    )
    st.session_state["num_semesters"] = num_semesters

    col_a, col_b = st.sidebar.columns(2)
    col_a.button("✨ Demo Data", on_click=fill_demo_data, width="stretch")
    col_b.button("🔄 Reset", on_click=reset_all, width="stretch")

    with st.sidebar.expander("💡 Quick Tips"):
        st.markdown(
            "- Toggle **off** semesters you haven't completed yet\n"
            "- The **what-if chart** updates live as you type\n"
            "- Try the 7 themes above — switching is instant\n"
            "- 'Auto' follows your system's light/dark setting\n"
        )

    return {"name": name, "university": university, "branch": branch, "year": year}


# --------------------------------------------------------------------------
# CSV Bulk Import (file_uploader + data_editor preview)
# --------------------------------------------------------------------------
def render_csv_import():
    """
    Let a student bulk-import semester data from a CSV (e.g. exported
    from their own tracking spreadsheet) instead of typing every
    semester by hand. Uses st.data_editor so they can fix a value
    before it's applied to the semester cards below.
    """
    with st.expander("📤  Already have your grades in a spreadsheet? Bulk-import from CSV →", expanded=False):
        st.caption(
            "Upload a CSV with **SGPA** and **Credits** columns (one row per semester). "
            "You can tweak values below before applying them."
        )
        uploaded = st.file_uploader("Choose a CSV file", type=["csv"], key="csv_uploader")

        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                df.columns = [c.strip().lower() for c in df.columns]
            except Exception as exc:
                st.error(f"Couldn't read that file as a CSV: {exc}")
                return

            if not {"sgpa", "credits"}.issubset(set(df.columns)):
                st.error("The CSV must contain at least an **sgpa** column and a **credits** column.")
                return

            preview_df = df[["sgpa", "credits"]].head(MAX_SEMESTERS).copy()
            edited_df = st.data_editor(
                preview_df, width="stretch", num_rows="fixed",
                key="csv_preview_editor",
                column_config={
                    "sgpa": st.column_config.NumberColumn("SGPA", min_value=0.0, max_value=10.0, step=0.01, format="%.2f"),
                    "credits": st.column_config.NumberColumn("Credits", min_value=1.0, max_value=40.0, step=1.0),
                },
            )

            if st.button("✅ Apply to Semester Cards", key="apply_csv_btn", width="stretch"):
                n = max(1, min(len(edited_df), MAX_SEMESTERS))
                st.session_state["num_semesters"] = n
                for i in range(n):
                    row = edited_df.iloc[i]
                    st.session_state[f"toggle_{i}"] = True
                    st.session_state[f"sgpa_{i}"] = float(row["sgpa"])
                    st.session_state[f"credit_{i}"] = float(row["credits"])
                st.toast(f"📥 Imported {n} semester(s) from CSV!", icon="📥")
                st.rerun()


# --------------------------------------------------------------------------
# CGPA Calculator Section (toggle + precise number-input semester cards)
# --------------------------------------------------------------------------
def render_calculator_section():
    """Render the toggle/number-input semester input grid and return raw values."""
    styling.eyebrow("Step 1 · Your Data")
    header_col, help1_col, help2_col = st.columns([3, 1, 1])
    header_col.markdown("#### 📊 Semester-wise Academic Data")
    with help1_col.popover("ℹ️ What's SGPA?"):
        st.markdown(
            "**SGPA** (Semester Grade Point Average) measures your academic "
            "performance in a *single semester* — the credit-weighted average "
            "of the grade points you earned in that semester's courses."
        )
    with help2_col.popover("ℹ️ What's CGPA?"):
        st.markdown(
            "**CGPA** (Cumulative Grade Point Average) is the credit-weighted "
            "average of your SGPA across *all* semesters completed so far — "
            "it reflects your overall academic standing."
        )

    st.caption("Toggle a semester **on** once you've completed it. Type an exact SGPA for instant grade feedback.")

    render_csv_import()

    sgpa_inputs = []
    credit_inputs = []

    n = st.session_state["num_semesters"]
    cols_per_row = 3

    for row_start in range(0, n, cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            sem_idx = row_start + i
            if sem_idx >= n:
                break
            with col:
                with st.container(border=True):
                    top_l, top_r = st.columns([2, 1])
                    top_l.markdown(f"**Semester {sem_idx + 1}**")
                    st.session_state.setdefault(f"toggle_{sem_idx}", False)
                    completed = top_r.toggle(
                        "On", key=f"toggle_{sem_idx}",
                        label_visibility="collapsed",
                    )

                    if completed:
                        st.session_state.setdefault(f"sgpa_{sem_idx}", DEFAULT_SGPA)
                        sgpa_val = st.number_input(
                            "SGPA", min_value=0.0, max_value=10.0,
                            step=0.01, format="%.2f", key=f"sgpa_{sem_idx}",
                            help="Type any value 0.00 - 10.00, e.g. 7.77",
                        )
                        st.session_state.setdefault(f"credit_{sem_idx}", DEFAULT_CREDITS)
                        credit_val = st.number_input(
                            "Credits", min_value=1.0, max_value=40.0,
                            step=1.0, key=f"credit_{sem_idx}",
                        )
                        grade = calculator.sgpa_to_grade(sgpa_val)
                        st.markdown(
                            f'<span class="grade-pill">{grade}</span>&nbsp;'
                            f'<span style="color:#94A3B8;font-size:0.8rem;">grade</span>',
                            unsafe_allow_html=True,
                        )
                        sgpa_inputs.append(sgpa_val)
                        credit_inputs.append(credit_val)
                    else:
                        st.caption("Not completed yet — toggle on to enter data")
                        sgpa_inputs.append(None)
                        credit_inputs.append(None)

    return sgpa_inputs, credit_inputs


# --------------------------------------------------------------------------
# Target Planner Section (with live what-if chart)
# --------------------------------------------------------------------------
def render_planner_section(preview_sgpas, preview_credits):
    """Render target CGPA + remaining credits inputs, plus a live what-if chart."""
    st.markdown("#### 🎯 Target CGPA Planner")
    col1, col2 = st.columns(2)
    with col1:
        target_cgpa = st.text_input(
            "Desired Final CGPA", placeholder="e.g. 8.5", key="target_cgpa_input",
            help="What CGPA do you want to graduate with?",
        )
    with col2:
        remaining_credits = st.text_input(
            "Total Remaining Credits", placeholder="e.g. 40", key="remaining_credits_input",
            help="Sum of credits across all semesters you haven't completed",
        )

    remaining_val = None
    if remaining_credits and validation.is_valid_credit(remaining_credits):
        remaining_val = float(remaining_credits)

    if preview_sgpas and remaining_val:
        theme_colors = styling.get_chart_colors(st.session_state["palette"])
        st.plotly_chart(
            ic.what_if_curve(preview_sgpas, preview_credits, remaining_val, colors=theme_colors),
            width="stretch", config={"displayModeBar": False},
            key="whatif_live_preview",
        )
        st.caption("👆 Live preview — updates instantly as you adjust semesters or remaining credits.")
    elif preview_sgpas:
        st.info("Enter your **remaining credits** above to see a live what-if curve.")

    return target_cgpa, remaining_credits


# --------------------------------------------------------------------------
# Dashboard Tab
# --------------------------------------------------------------------------
def render_dashboard(calc_result):
    """Render the summary metric cards + interactive charts."""
    styling.eyebrow("Your Results")
    cgpa = calc_result["cgpa"]
    prev = st.session_state.get("prev_cgpa")
    delta_txt = f"{cgpa - prev:+.2f} vs last run" if prev is not None and prev != cgpa else ""

    c1, c2, c3, c4 = st.columns([1.3, 1.3, 0.9, 0.9])
    with c1:
        styling.score_badge(cgpa, 10, "Current CGPA")
        if delta_txt:
            st.caption(delta_txt)
    with c2:
        styling.percentage_formula_card([
            {"name": "UGC Formula", "expr": "(CGPA − 0.75) × 10", "value": f"{calc_result['percentage_ugc']:.2f}%"},
            {"name": "Direct 10× Formula", "expr": "CGPA × 10", "value": f"{calc_result['percentage']:.2f}%"},
        ])
    with c3:
        styling.glass_metric("Completed Credits", f"{calc_result['total_credits']:.0f}")
    with c4:
        styling.glass_metric("Overall Grade", calculator.sgpa_to_grade(cgpa))

    st.session_state["prev_cgpa"] = cgpa
    st.write("")

    if calc_result["semester_summary"]:
        sgpa_list = [row["SGPA"] for row in calc_result["semester_summary"]]
        credit_list = [row["Credits"] for row in calc_result["semester_summary"]]
        theme_colors = styling.get_chart_colors(st.session_state["palette"])

        target = st.session_state.get("target_cgpa")
        gcol, tcol = st.columns([1, 1.3])
        with gcol:
            st.plotly_chart(ic.cgpa_gauge(cgpa, target, colors=theme_colors), width="stretch", config={"displayModeBar": False}, key="cgpa_gauge_dashboard")
        with tcol:
            st.plotly_chart(ic.sgpa_trend_chart(sgpa_list, colors=theme_colors), width="stretch", config={"displayModeBar": False}, key="sgpa_trend_dashboard")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(ic.semester_performance_chart(sgpa_list, colors=theme_colors), width="stretch", config={"displayModeBar": False}, key="sem_perf_dashboard")
        with chart_col2:
            st.plotly_chart(ic.credit_distribution_chart(credit_list, colors=theme_colors), width="stretch", config={"displayModeBar": False}, key="credit_dist_dashboard")

        st.markdown("##### 📋 Semester-wise Record")
        st.dataframe(calc_result["semester_summary"], width="stretch", hide_index=True)
    else:
        st.info("Enter at least one completed semester to see your dashboard.")


# --------------------------------------------------------------------------
# Target Result Tab
# --------------------------------------------------------------------------
def render_target_tab(planner_result, target_cgpa):
    styling.eyebrow("Future Planning")
    if planner_result is None:
        st.info("💡 Fill in **Desired Final CGPA** and **Remaining Credits** above, then hit Calculate to see your plan.")
        return

    achievable = planner_result["achievable"]
    kind = "success" if achievable else "danger"
    label = "Achievable ✅" if achievable else "Not Achievable ❌"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Status**<br>{styling.badge(label, kind)}", unsafe_allow_html=True)
    with c2:
        styling.glass_metric("Target CGPA", f"{target_cgpa:.2f}")
    with c3:
        req = planner_result["required_sgpa"]
        styling.glass_metric("Required Future SGPA", f"{req}" if req is not None else "—")

    st.write("")
    if achievable:
        st.success(planner_result["message"])
    else:
        st.warning(planner_result["message"])

    sgpas = st.session_state.get("clean_sgpas", [])
    credits = st.session_state.get("clean_credits", [])
    remaining = st.session_state.get("remaining_credits", 0)
    if sgpas and remaining:
        theme_colors = styling.get_chart_colors(st.session_state["palette"])
        st.plotly_chart(ic.what_if_curve(sgpas, credits, remaining, colors=theme_colors), width="stretch", config={"displayModeBar": False}, key="whatif_target_tab")


# --------------------------------------------------------------------------
# AI Advisor Tab
# --------------------------------------------------------------------------
def render_ai_advisor(ai_result):
    """Render the AI Academic Advisor's recommendations."""
    styling.eyebrow("Powered by Machine Learning")
    trend_kind = {"Improving": "success", "Stable": "info", "Declining": "danger"}.get(ai_result["trend"], "info")
    chance_kind = {"High": "success", "Medium": "warning", "Low": "danger"}.get(ai_result["chance_label"], "info")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Performance Level**<br>{styling.badge(ai_result['performance_level'], 'purple')}", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**Trend**<br>{styling.badge(ai_result['trend'], trend_kind)}", unsafe_allow_html=True)
    with c3:
        st.markdown(f"**Chance of Achieving Target**<br>{styling.badge(ai_result['chance_label'], chance_kind)}", unsafe_allow_html=True)

    st.write("")
    theme_colors = styling.get_chart_colors(st.session_state["palette"])
    rcol, gcol = st.columns([1.4, 1])
    with rcol:
        st.plotly_chart(
            ic.advisor_radar(
                avg_sgpa=sum(st.session_state["clean_sgpas"]) / len(st.session_state["clean_sgpas"]),
                consistency_std=ai_result["consistency_std"],
                trend_slope=ai_result["trend_slope"],
                chance_label=ai_result["chance_label"],
                colors=theme_colors,
            ),
            width="stretch", config={"displayModeBar": False},
            key="advisor_radar_chart",
        )
    with gcol:
        st.markdown("###### Success Likelihood")
        st.plotly_chart(ic.chance_gauge(ai_result["chance_label"], colors=theme_colors), width="stretch", config={"displayModeBar": False}, key="chance_gauge_advisor")

    st.markdown("##### 📌 Study Suggestions")
    icons = ["📚", "📈", "🎯", "💡", "⚠️", "✅"]
    for i, suggestion in enumerate(ai_result["suggestions"]):
        styling.suggestion_card(icons[i % len(icons)], suggestion)

    st.write("")
    fcol1, fcol2 = st.columns([1, 3])
    with fcol1:
        sentiment = st.feedback("thumbs", key="advisor_feedback")
    with fcol2:
        st.caption("Were these suggestions helpful?")
        if sentiment is not None:
            if sentiment == 1:
                st.toast("Glad it helped! 🎉", icon="🎉")
            else:
                st.toast("Thanks — we'll keep refining these suggestions.", icon="🙏")


# --------------------------------------------------------------------------
# Export Report Tab
# --------------------------------------------------------------------------
def render_export_tab():
    styling.eyebrow("Take It With You")
    st.markdown("##### 📄 Download Your Full Academic Report")
    st.caption("Includes student details, semester table, CGPA/percentage, target planning, AI recommendations, and charts.")

    if st.button("🖨️ Generate PDF Report", type="primary", width="stretch"):
        with st.spinner("Building your personalized report..."):
            tmp_path = os.path.join(tempfile.gettempdir(), "cgpa_report.pdf")
            pdf_generator.generate_pdf_report(
                output_path=tmp_path,
                student_info=st.session_state["student_info"],
                calculator_result=st.session_state["calc_result"],
                target_cgpa=st.session_state["target_cgpa"],
                planner_result=st.session_state["planner_result"],
                ai_result=st.session_state["ai_result"],
                sgpa_list=st.session_state["clean_sgpas"],
                credit_list=st.session_state["clean_credits"],
            )
            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()
        st.toast("📄 Report ready!", icon="📄")
        st.download_button(
            "⬇️ Download PDF Report", data=pdf_bytes, file_name="CGPA_Academic_Report.pdf",
            mime="application/pdf", width="stretch",
        )


def render_how_it_works():
    """Render a 4-step numbered 'How It Works' row explaining the app's flow."""
    st.write("")
    styling.eyebrow("The Process")
    st.markdown("#### How It Works")
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("01", "Enter Your Data", "Toggle on each completed semester and type your exact SGPA and credits."),
        ("02", "Set a Target", "Optionally enter your dream final CGPA and remaining credits to plan ahead."),
        ("03", "AI Analysis", "Our trained model reads your trend, consistency, and target difficulty."),
        ("04", "Export & Track", "Download a polished PDF report with charts, insights, and suggestions."),
    ]
    for col, (num, title, desc) in zip([c1, c2, c3, c4], steps):
        with col:
            styling.step_card(num, title, desc)


# --------------------------------------------------------------------------
# Main App Flow
# --------------------------------------------------------------------------
def main():
    student_info = render_sidebar()

    styling.eyebrow("Academic Intelligence Platform")
    styling.hero_banner(
        "🎓 Smart CGPA Calculator & AI Academic Advisor",
        "Calculate your CGPA, plan future semesters, and get AI-powered academic recommendations — "
        "grounded in transparent math, backed by a trained ML model.",
        accent_word="AI Academic Advisor",
    )
    styling.marquee([
        "🧮 100% Transparent CGPA Math",
        "🤖 99.2% Advisor Model Accuracy",
        "📊 1,200 Training Profiles",
        "🎯 2-Decimal SGPA Precision",
        "📄 One-Click PDF Reports",
        "🔒 Your Data Stays In-Session",
    ])

    render_how_it_works()
    st.write("")

    with st.container(border=True):
        sgpa_inputs, credit_inputs = render_calculator_section()

    preview_sgpas, preview_credits, _ = validation.validate_semesters(sgpa_inputs, credit_inputs)

    with st.container(border=True):
        target_cgpa_raw, remaining_credits_raw = render_planner_section(preview_sgpas, preview_credits)

    st.write("")
    calculate_clicked = st.button("🚀 Calculate & Analyze", type="primary", width="stretch")

    if calculate_clicked:
        with st.status("Running your analysis...", expanded=True) as status:
            errors = []

            st.write("🔍 Validating your inputs...")
            student_errors = validation.validate_student_info(
                student_info["name"], student_info["university"],
                student_info["branch"], student_info["year"],
            )
            errors.extend(student_errors)

            clean_sgpas, clean_credits, semester_errors = validation.validate_semesters(
                sgpa_inputs, credit_inputs
            )
            errors.extend(semester_errors)

            if not clean_sgpas:
                errors.append("Please enter at least one valid completed semester.")

            target_cgpa = None
            remaining_credits = 0.0
            planner_result = None

            target_provided = bool(target_cgpa_raw and str(target_cgpa_raw).strip())
            if target_provided:
                is_valid_target, target_error = validation.validate_target_cgpa(target_cgpa_raw)
                if not is_valid_target:
                    errors.append(target_error)
                else:
                    target_cgpa = float(target_cgpa_raw)

                if remaining_credits_raw and str(remaining_credits_raw).strip():
                    if not validation.is_valid_credit(remaining_credits_raw):
                        errors.append("Remaining credits must be a positive number.")
                    else:
                        remaining_credits = float(remaining_credits_raw)
                else:
                    errors.append("Please enter remaining credits to use the Target Planner.")

            if errors:
                status.update(label="Validation failed", state="error", expanded=True)
                for err in errors:
                    st.error(err)
                st.session_state["results_ready"] = False
            else:
                st.write("🧮 Calculating CGPA & percentage...")
                calc_result = calculator.calculate_full_report(clean_sgpas, clean_credits)

                if target_cgpa is not None:
                    st.write("🎯 Solving target CGPA planner...")
                    planner_result = planner.calculate_required_sgpa(
                        clean_sgpas, clean_credits, remaining_credits, target_cgpa
                    )

                st.write("🤖 Running AI Academic Advisor model...")
                ai_result = advisor.get_ai_recommendation(
                    sgpa_list=clean_sgpas,
                    completed_credits=calc_result["total_credits"],
                    remaining_credits=remaining_credits,
                    target_cgpa=target_cgpa if target_cgpa is not None else calc_result["cgpa"],
                    required_sgpa=planner_result["required_sgpa"] if planner_result else None,
                )

                st.session_state.update(
                    {
                        "results_ready": True,
                        "clean_sgpas": clean_sgpas,
                        "clean_credits": clean_credits,
                        "calc_result": calc_result,
                        "planner_result": planner_result,
                        "ai_result": ai_result,
                        "target_cgpa": target_cgpa,
                        "remaining_credits": remaining_credits,
                        "student_info": student_info,
                    }
                )
                status.update(label="Analysis complete!", state="complete", expanded=False)

        if st.session_state["results_ready"]:
            st.toast("🎉 Calculation complete!", icon="🎉")
            if st.session_state["ai_result"]["performance_level"] == "Excellent":
                st.balloons()

    if st.session_state["results_ready"]:
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Dashboard", "🎯 Target Result", "🤖 AI Advisor", "📄 Export Report"]
        )
        with tab1:
            render_dashboard(st.session_state["calc_result"])
        with tab2:
            render_target_tab(st.session_state["planner_result"], st.session_state["target_cgpa"] or 0.0)
        with tab3:
            render_ai_advisor(st.session_state["ai_result"])
        with tab4:
            render_export_tab()


if __name__ == "__main__":
    main()
