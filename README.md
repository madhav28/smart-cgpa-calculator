# 🎓 Smart CGPA Calculator & AI Academic Advisor

A professional Streamlit web application that helps university students
calculate their current CGPA and percentage, plan future semesters to hit a
target CGPA, and receive AI-powered academic recommendations — complete with
a downloadable PDF report.

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
| 🌓 **Auto** | Follows your OS | Mirrors Aurora (dark) / Light Academic (light) via a pure-CSS `prefers-color-scheme` media query — works even without JavaScript |

All animations only animate `transform`/`opacity`/`background-position`
(cheap, GPU-friendly properties) and run slow (24–40s loops), per the
"lightweight, non-distracting" brief. `@media (prefers-reduced-motion:
reduce)` disables them for users who've asked their OS to reduce motion.

> **Implementation note:** the animated background is painted as native
> CSS `background-image` layers directly on Streamlit's own
> `[data-testid="stAppViewContainer"]` element — not as a separate
> `position: fixed` `<div>` injected via `st.markdown()`. An earlier
> version used the latter, and the background silently failed to render
> (themes only changed accent colors, not the backdrop): a
> `position: fixed` element nested deep inside Streamlit's own component
> tree gets clipped by any ancestor managing its own scroll/overflow — a
> well-known CSS gotcha, and exactly what Streamlit's main content area
> does. Painting directly on the container Streamlit itself renders
> avoids that failure mode entirely, and was verified by pixel-sampling
> the background color across all 7 themes to confirm it actually
> changes (not just the accent/text colors on top of it). The drift
> keyframe also swings each blob much further (~15–20% across 5 steps,
> not ~5%) so the motion is clearly visible rather than imperceptibly
> subtle, and `animation` carries `!important` as a defensive measure.

> **Fixed bug — raw HTML briefly visible in the hero banner:** an
> earlier version built the hero banner's HTML as a multi-line, indented
> Python f-string. Markdown treats a generic `<div>` as an "HTML block"
> that ends at the first **blank line** — and interpolating a helper
> string that itself started with a leading `\n` (the SVG cap icon)
> created exactly such a blank line right after the opening `<div>`,
> causing everything after it to render as literal escaped text instead
> of HTML. `<style>` blocks are immune to this (they're a different,
> special-cased HTML block type that only ends at a literal `</style>`),
> which is why the CSS injection was never affected — only the hero
> banner was. Every HTML-emitting helper in `modules/styling.py` is now
> built as a single flat string with zero embedded newlines, and a
> regression test asserts this for all of them so the bug class can't
> quietly return.

> **Fixed bug — `check_session_state_rules` warning/crash on the
> semester toggles and theme picker:** several widgets passed **both**
> `key=` and `value=`/`index=` where the value was read straight out of
> `st.session_state[key]` itself (e.g.
> `st.toggle(..., key=f"toggle_{i}", value=st.session_state.get(f"toggle_{i}", False))`).
> On the first run this is harmless, but once Streamlit has persisted a
> value under that key (i.e. every rerun after the first), passing an
> explicit `value=`/`index=` *on top of* an already-populated `key=` is
> an ambiguous, explicitly-disallowed pattern — it's the same root cause
> as the earlier `text_input` type-mismatch crash, just surfacing
> through a different widget. Every occurrence (the semester toggles,
> the SGPA/credit number inputs, and the theme `selectbox`) now seeds
> `st.session_state` once via `.setdefault()` *before* the widget call
> and passes only `key=` — session_state is the single source of truth
> from then on. A regression test now statically scans every widget
> call in `app.py` for this exact conflict.

> **Fixed — Light Academic theme looked like a dark component on a
> light background.** The sidebar's headings were barely visible, input
> boxes rendered as muddy gray boxes with harsh dark borders, the
> number-input +/− buttons and progress bar stayed solid black, and the
> sidebar had a visible hard edge. Root causes and fixes:
> - Heading/text colors were only set via a low-specificity `color`
>   rule (no `!important`), so Streamlit's own higher-specificity
>   internal styling could win. Now forced with `!important` and
>   explicit `[data-testid="stMarkdownContainer"] h1–h4` selectors.
> - Inputs used the same semi-transparent `--surface` value as glass
>   cards; on a light theme, that transparency blended with Streamlit's
>   own (dark-by-default) input chrome underneath and read as gray. A
>   new `--input-bg` variable is fully opaque on light themes (and
>   unchanged on dark ones, where it already looked fine).
> - The sidebar's `box-shadow` was never explicitly cleared, so a
>   dark drop-shadow meant for the dark theme persisted; now set to
>   `none` and the border softened to match the theme.
> - The number-input stepper buttons and `st.progress()` bar were never
>   themed at all (always black/violet regardless of theme) — both now
>   use `--input-bg`/`--gradient` like everything else.
> - **Follow-up fix:** two of four *identical* sidebar text inputs
>   ("University," "Branch") still rendered dark while others didn't —
>   because the browser recognized them as previously-saved values and
>   applied its own autofill background, via an internal mechanism
>   ordinary `background-color`/`!important` can't reach. Fixed with the
>   standard `:-webkit-autofill` inset-box-shadow override.
> - **Follow-up fix:** the profile-completion progress bar showed a
>   full-width gradient "pill" with the label text sitting inside it,
>   stacked above the real (correctly proportioned) bar. The original
>   CSS targeted a generic `> div > div` nesting guess, which also
>   matched the text-caption element Streamlit renders alongside the
>   bar. Rescoped to `[role="progressbar"]` — the semantic ARIA role,
>   which can only match the actual bar, not the caption.
> - **Follow-up fix:** the semester toggle switch was invisible until
>   hovered. It had zero custom CSS before this fix — its track relied
>   entirely on Streamlit's dark-base-theme-derived default colors,
>   which on Light Academic were close enough to the light background
>   to be nearly invisible at rest, only appearing once BaseWeb's
>   hover-only outline kicked in. Fixed by giving the idle state the
>   *same* explicit, theme-aware styling as the hover state, so there's
>   no visibility gap between them at all.

**Final-phase audit** (a full pass looking for anything else in the same
family of bug, not just the two reported issues):
- **Found and fixed independently:** chart hover tooltips had a fixed
  dark background but *theme-dependent* text color — on Light Academic
  that meant dark-navy text on a dark tooltip, illegible. Tooltip text
  color is now fixed light, matching the fixed dark tooltip background,
  regardless of theme (a tooltip overlay doesn't need to follow the
  page theme to read well).
- **Added coverage for widgets that had no custom styling at all**
  before this pass and could plausibly have shown the same
  "dark-theme-derived color on a light page" problem: the selectbox's
  own dropdown menu (a portal element, not nested in the widget's DOM —
  relevant since it's literally what renders the theme picker itself),
  the file uploader, `st.popover` content, and the `st.status()`
  processing container.
- **Known, disclosed limitation:** `st.dataframe`/`st.data_editor`
  render their cell contents on an HTML5 canvas (glide-data-grid) —
  canvas pixels aren't part of the DOM, so CSS cannot recolor them.
  These two tables will keep following Streamlit's fixed `config.toml`
  base theme internally regardless of the active app theme. The
  container *frame* around them is themed to look intentional rather
  than like an unstyled gap; a pixel-perfect per-theme recolor of the
  grid's internals would require swapping to a plain HTML table instead
  (losing sortability), which I haven't done since it wasn't reported
  as broken and changes behavior, not just styling.
- Re-ran the full regression suite: compile checks, a static scan for
  the `key=`/`value=` conflict across every widget, a scan for
  deprecated Streamlit APIs, all 7 themes through 2 reruns each, the
  Demo Data crash scenario, the reset path, CSV import (valid and
  malformed), PDF generation, all chart functions across all themes,
  and the zero-embedded-newline check on every HTML component — all
  pass.

---

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
