# 🎓 Smart CGPA Calculator & AI Academic Advisor

A professional Streamlit web application that helps university students
calculate their current CGPA and percentage, plan future semesters to hit a
target CGPA, and receive AI-powered academic recommendations — complete with
a downloadable PDF report.

---
Live Demo - https://smart-cgpa-calculator.streamlit.app/
---

## ✨ Features

| Feature | Description |
|---|---|
| **Student Information** | Capture name, university, branch, admission year — with a live "profile completeness" progress bar |
| **CGPA Calculator** | Toggle-based semester cards (flip a semester "on" once completed), sliders with instant letter-grade badges, validates all inputs, computes weighted CGPA and percentage |
| **Target CGPA Planner** | Pure-math calculation of the SGPA required in remaining semesters to hit a desired final CGPA, with a **live "what-if" chart** that updates as you type — no button click required |
| **AI Academic Advisor** | ML-based analysis of performance trend, consistency, performance level, and chance of achieving the target, visualized as a radar chart + gauge, plus study suggestion cards |
| **Dashboard** | Glassmorphic KPI cards, a CGPA speedometer gauge, and interactive Plotly charts (SGPA trend, semester performance, credit distribution donut) with hover tooltips and zoom |
| **PDF Report** | Downloadable report with student details, semester table, CGPA/percentage, target planning, AI recommendations, and charts |
| **Validation** | Range checks, positivity checks, graceful handling of invalid/empty input |

> **Note:** Machine Learning is used **only** for the AI Academic Advisor's
> recommendations. All CGPA, percentage, and target-planning calculations are
> pure, transparent mathematics (see `modules/calculator.py` and
> `modules/planner.py`).

---

## 🎨 Premium SaaS Design System

The interface follows a premium, AI-product dashboard aesthetic — dark
glass cards, animated abstract backgrounds, gradient accents, and
generous spacing. Everything is built from CSS gradients, CSS
animations, and inline SVG — **no photographs, no external image
assets, nothing borrowed from any third party.**

### 7-theme system, instant switching, no restart

Pick a theme from the sidebar dropdown and the whole app — background,
accents, buttons, cards, sidebar, hero glow, and **chart color
palettes** — updates immediately on the next rerun. No page reload, no
Streamlit restart, because theming is pure CSS-variable injection
(`modules/styling.py`), not a `config.toml` change.

| Theme | Feel | Animated background |
|---|---|---|
| 🟣 **Aurora** | Dark navy, purple-blue glow | 3 slow-drifting blurred blobs, soft floating light |
| 🔵 **Ocean** | Deep blue, cyan glow | Blobs + a faint neural-network dot/line pattern |
| 🟢 **Emerald** | Dark green | Blobs + a faint animated digital grid |
| 🟠 **Sunset** | Dark orange-red | Blobs + a slow-shifting warm gradient wave |
| ⚫ **Midnight** | Near-black, blue glow | Blobs + a tiled starfield with a gentle twinkle |
| ⚪ **Light Academic** | White, soft blue | Light blobs + a faint geometric line pattern |
| 🌓 **Auto** | Follows your OS | Mirrors Aurora (dark) / Light Academic (light) via a pure-CSS `prefers-color-scheme` media query — works even without JavaScript 

### Other visual highlights

- **Glassmorphism** on every card (`rgba` translucent background,
  `backdrop-filter: blur(20px)`, soft hairline border, 18–24px radius),
  matching the exact CSS values requested
- **Poppins** for headings, **Inter** for body text
- **Small floating graduation-cap illustration** (original inline SVG,
  gradient-filled, gentle bob animation) + a handful of ambient floating
  particles in the hero
- **Gradient buttons** with hover-lift, scale, and glow — accent color
  always matches the active theme
- **Redesigned sidebar** — translucent, blurred, theme-tinted, with
  glowing hover states on expanders/cards
- **Numbered "How It Works" step cards**, a scrolling credential
  marquee, and a big "Score X.XX / 10" badge for the headline CGPA
- **Toggle + precise number-input semester entry** — flip a semester
  "on," type an exact SGPA (e.g. 7.77), see an instant letter-grade pill
- **CSV bulk import** — upload a spreadsheet export, fix values inline
  with `st.data_editor`, apply to all semester cards in one click
- **Contextual glossary popovers** ("What's SGPA?" / "What's CGPA?")
- **Live "what-if" chart** — updates as you type, before you click Calculate
- **Interactive Plotly visuals** — hoverable charts, a CGPA speedometer
  gauge, a success-likelihood gauge, and a 4-axis radar chart, all
  recolored per theme (chart **data** is untouched — see below)
- **`st.status()` processing feed**, **`st.feedback`** thumbs rating,
  toast notifications, and confetti (`st.balloons()`) on strong results
- **Tabbed results** (`📊 Dashboard` / `🎯 Target Result` / `🤖 AI Advisor` /
  `📄 Export Report`) instead of one long scroll
- **Visible focus outlines** on every interactive element and
  color-paired status badges (never color alone) for accessibility
- **One-click demo data / reset** buttons for instant, low-friction trial

Every `st.plotly_chart` call carries an explicit, unique `key=` —
required so Streamlit doesn't raise a `StreamlitDuplicateElementId`
error when two charts render with identical parameters.

> **Where's the CSV importer?** Open the **"Semester-wise Academic Data"**
> card (below "How It Works") and look for the bordered expander labeled
> *"📤 Already have your grades in a spreadsheet? Bulk-import from CSV →"*
> right under the caption. Click it, upload a CSV with `SGPA` and
> `Credits` columns, fix anything inline in the editable preview table,
> then hit **"✅ Apply to Semester Cards"** to fill in all your semesters
> at once instead of typing each one by hand.

### What was deliberately left untouched

Per the design brief, **no business logic was modified**: the CGPA/
percentage math, the target planner's algebra, the AI Advisor's model
and feature engineering, input validation rules, CSV parsing logic, PDF
report generation/content, dashboard tab order, and the overall
workflow are all byte-for-byte the same as before this redesign.
`modules/interactive_charts.py` now accepts an optional `colors=` dict
so charts can be recolored per theme — every chart's underlying data,
axes, and computed values were verified identical (old output vs. new
output, trace-by-trace) before and after this change.

---

## 🧹 Streamlit Modernization

`use_container_width` is deprecated across Streamlit — and, as of
Streamlit's 2026 releases, has already been **fully removed** from
`st.plotly_chart` and `st.vega_lite_chart` (not just warned-about). The
entire project was searched and every occurrence replaced:

- `use_container_width=True` → `width="stretch"`
- `use_container_width=False` → `width="content"` *(not applicable here — this project only ever used `=True`)*

`requirements.txt` now pins `streamlit>=1.51.0` to guarantee `width=`
support across `st.button`, `st.download_button`, `st.dataframe`,
`st.data_editor`, and `st.plotly_chart`.

---

## 🧮 Core Formulas

```
CGPA                 = Σ(SGPA × Credits) / Σ(Credits)
Percentage (Direct)  = CGPA × 10
Percentage (UGC)     = (CGPA − 0.75) × 10

Required SGPA (Target Planner):
    Required_SGPA = (Target_CGPA × Total_Credits − Σ(Completed_SGPA × Completed_Credits))
                     / Remaining_Credits
```

The dashboard shows **both** percentage conversions side by side, since
different universities officially use different formulas — neither is
"more correct." `calculator.calculate_full_report()` returns both under
separate keys (`percentage` = Direct 10x, `percentage_ugc` = UGC), so
existing code reading `["percentage"]` is unaffected. The display itself
(`styling.percentage_formula_card()`) takes a plain list of
`{name, expr, value}` dicts — dropping to a single formula (if a
university only uses one) is just passing a one-item list; the divider
between rows only appears when there are two or more.

---

## 🗂️ Project Structure

```
app.py                          # Streamlit UI (thin layer, no business logic)
modules/
    calculator.py                # CGPA / percentage math
    planner.py                   # Target CGPA math
    advisor.py                   # ML-based AI Academic Advisor
    validation.py                # Centralized input validation
    graphs.py                    # Matplotlib static charts (used by the PDF export)
    interactive_charts.py        # Plotly interactive charts (theme-aware colors, used by the live dashboard)
    styling.py                   # 7-theme system: animated backgrounds, CSS, reusable UI components
    pdf_generator.py             # ReportLab PDF report builder
models/
    train_model.py                # Trains & saves the ML advisor model
    advisor_model.pkl             # Trained model bundle (joblib)
dataset/
    student_dataset.csv           # Synthetic historical training data
    generate_dataset.py           # Script used to generate the dataset
assets/                          # Static assets (logos, icons, etc.)
requirements.txt
README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Retrain the AI Advisor model

A pre-trained model is already included at `models/advisor_model.pkl`. To
regenerate the dataset and retrain from scratch:

```bash
python dataset/generate_dataset.py
python models/train_model.py
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🤖 How the AI Advisor Works

1. **Feature engineering (deterministic math, not ML):**
   - Average SGPA, standard deviation (consistency), and trend slope
     (via linear regression over semester index vs. SGPA).
2. **ML inference:**
   - A `RandomForestClassifier` predicts **Performance Level**
     (Excellent / Good / Average / Below Average).
   - A second `RandomForestClassifier` predicts **Chance of Achieving
     Target** (High / Medium / Low), using the required SGPA from the
     (non-ML) planner as one of its inputs.
3. **Study suggestions:**
   - Generated with transparent, rule-based logic from the model's
     predictions — keeping recommendations explainable.

Both classifiers are trained on a synthetic dataset of 1,200 simulated
student academic histories (`dataset/student_dataset.csv`) covering
improving, declining, and stable performance trends.

---

## ✅ Validation Rules

- SGPA must be between **0 and 10**.
- Credits must be a **positive number**.
- Semesters left completely blank are **ignored** (not treated as errors).
- Partially filled semesters (one field filled, one blank) raise a
  clear validation error.
- Target CGPA must also be between 0 and 10.

---

## 🧱 Coding Standards

- PEP8-compliant, documented, modular code.
- UI (`app.py`) is fully separated from business logic (`modules/`).
- No duplicate logic — shared helpers (e.g. `calculate_cgpa`) are reused
  across the calculator, planner, advisor, and PDF generator.

---

## 🔭 Future Scope

- **Backend:** FastAPI service layer for a proper client-server architecture.
- **Database:** MySQL for persistent storage of student records.
- **Authentication:** User login / registration system.
- **History:** Track and compare CGPA calculations over time.
- **Admin Dashboard:** Aggregate analytics across all students.
- **Cloud Deployment:** Deploy to Streamlit Community Cloud / AWS / Azure.
- **CI/CD:** GitHub Actions for automated testing and deployment.

---

## 📄 License

This project is provided as-is for educational purposes.
