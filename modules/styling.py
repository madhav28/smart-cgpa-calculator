"""
styling.py
----------
Centralized custom CSS + small UI helper components for the Streamlit
app. Keeping all styling in one place means app.py stays focused on
layout/flow, per the "keep UI and logic separate" coding standard.
This module contains ONLY presentation code — no calculation, validation,
planner, advisor, or chart-data logic lives here.

Design direction: a premium SaaS aesthetic (dark-glass cards, animated
abstract backgrounds, gradient accents, generous spacing) in the spirit
of modern AI-product dashboards. Every visual is built from CSS
gradients, CSS animations, and inline SVG — no photographs, no external
image assets, nothing borrowed from any third party.

THEME SYSTEM
------------
`THEMES` defines 7 selectable themes (Aurora, Ocean, Emerald, Sunset,
Midnight, Light Academic, Auto). Each theme is a dict of CSS custom
property values (colors, gradients, surface treatment) plus a "texture"
key selecting which animated background pattern to layer over 3 slow
drifting glow blobs. Switching themes only changes which values are
written into `:root` on the next rerun — the DOM structure, layout, and
every business-logic module are completely untouched, so switching is
instant and never requires restarting Streamlit.

"Auto" reuses Aurora's values as its base (so it still renders correctly
without any browser support) and additionally emits `@media
(prefers-color-scheme: ...)` blocks so the browser itself can swap to a
light or dark variant based on the user's OS setting — no JS required.

IMPLEMENTATION NOTE: the animated background is painted as native CSS
`background-image` layers directly on Streamlit's own
`[data-testid="stAppViewContainer"]` element — NOT as a separate
`position: fixed` `<div>` injected via `st.markdown()`. An earlier
version used the latter and the background silently failed to render:
a `position: fixed` element nested deep inside Streamlit's own
component tree gets clipped by any ancestor that manages its own
scroll/overflow (a well-known CSS gotcha), which is exactly what
Streamlit's main content area does. Painting directly on the container
Streamlit itself renders avoids that failure mode entirely.
"""

import streamlit as st

# --------------------------------------------------------------------------
# Theme definitions
# --------------------------------------------------------------------------
THEMES = {
    "Aurora": {
        "mode": "dark",
        "primary": "#8B5CF6", "secondary": "#EC4899", "accent": "#22D3EE",
        "gradient": "linear-gradient(135deg, #8B5CF6 0%, #6366F1 55%, #EC4899 100%)",
        "glow": "rgba(139, 92, 246, 0.38)",
        "bg_base": "#0A0A16", "bg_base2": "#12102B",
        "surface": "rgba(255,255,255,0.07)", "surface_hover": "rgba(255,255,255,0.11)",
        "border": "rgba(255,255,255,0.15)",
        "text_primary": "#F5F5F8", "text_muted": "#A6A6C6",
        "on_accent": "#0B0C10",
        "blob1": "#8B5CF6", "blob2": "#6366F1", "blob3": "#EC4899",
        "texture": "none",
        "chart": {"primary": "#8B5CF6", "secondary": "#EC4899", "accent": "#22D3EE",
                   "good": "#34D399", "warn": "#FBBF24", "bad": "#F87171",
                   "grid": "rgba(255,255,255,0.09)", "text": "#E7E7F2"},
    },
    "Ocean": {
        "mode": "dark",
        "primary": "#0EA5E9", "secondary": "#22D3EE", "accent": "#38BDF8",
        "gradient": "linear-gradient(135deg, #0EA5E9 0%, #22D3EE 100%)",
        "glow": "rgba(14, 165, 233, 0.38)",
        "bg_base": "#050F1A", "bg_base2": "#082238",
        "surface": "rgba(255,255,255,0.06)", "surface_hover": "rgba(255,255,255,0.10)",
        "border": "rgba(255,255,255,0.13)",
        "text_primary": "#EAF6FF", "text_muted": "#8FB4CC",
        "on_accent": "#04141F",
        "blob1": "#0EA5E9", "blob2": "#22D3EE", "blob3": "#0369A1",
        "texture": "network",
        "chart": {"primary": "#0EA5E9", "secondary": "#38BDF8", "accent": "#67E8F9",
                   "good": "#2DD4BF", "warn": "#FBBF24", "bad": "#FB7185",
                   "grid": "rgba(255,255,255,0.08)", "text": "#DCEEF9"},
    },
    "Emerald": {
        "mode": "dark",
        "primary": "#10B981", "secondary": "#34D399", "accent": "#A3E635",
        "gradient": "linear-gradient(135deg, #10B981 0%, #34D399 55%, #A3E635 100%)",
        "glow": "rgba(16, 185, 129, 0.35)",
        "bg_base": "#04120C", "bg_base2": "#062018",
        "surface": "rgba(255,255,255,0.06)", "surface_hover": "rgba(255,255,255,0.10)",
        "border": "rgba(255,255,255,0.13)",
        "text_primary": "#EFFDF6", "text_muted": "#8FC7AC",
        "on_accent": "#04140D",
        "blob1": "#10B981", "blob2": "#059669", "blob3": "#A3E635",
        "texture": "grid",
        "chart": {"primary": "#10B981", "secondary": "#34D399", "accent": "#A3E635",
                   "good": "#4ADE80", "warn": "#FACC15", "bad": "#F87171",
                   "grid": "rgba(255,255,255,0.08)", "text": "#E3FBEF"},
    },
    "Sunset": {
        "mode": "dark",
        "primary": "#F97316", "secondary": "#F43F5E", "accent": "#FBBF24",
        "gradient": "linear-gradient(135deg, #F97316 0%, #F43F5E 60%, #FBBF24 100%)",
        "glow": "rgba(249, 115, 22, 0.35)",
        "bg_base": "#170A08", "bg_base2": "#26100B",
        "surface": "rgba(255,255,255,0.06)", "surface_hover": "rgba(255,255,255,0.10)",
        "border": "rgba(255,255,255,0.13)",
        "text_primary": "#FDF3EE", "text_muted": "#CBA294",
        "on_accent": "#170A08",
        "blob1": "#F97316", "blob2": "#F43F5E", "blob3": "#FBBF24",
        "texture": "waves",
        "wave_shift": "9% 6%",
        "chart": {"primary": "#F97316", "secondary": "#F43F5E", "accent": "#FBBF24",
                   "good": "#4ADE80", "warn": "#FBBF24", "bad": "#F43F5E",
                   "grid": "rgba(255,255,255,0.08)", "text": "#FBEAE2"},
    },
    "Midnight": {
        "mode": "dark",
        "primary": "#6366F1", "secondary": "#3B82F6", "accent": "#93C5FD",
        "gradient": "linear-gradient(135deg, #6366F1 0%, #3B82F6 100%)",
        "glow": "rgba(99, 102, 241, 0.35)",
        "bg_base": "#040406", "bg_base2": "#0B0B14",
        "surface": "rgba(255,255,255,0.055)", "surface_hover": "rgba(255,255,255,0.09)",
        "border": "rgba(255,255,255,0.12)",
        "text_primary": "#F2F2F7", "text_muted": "#9496B5",
        "on_accent": "#04040A",
        "blob1": "#6366F1", "blob2": "#3B82F6", "blob3": "#1E1B4B",
        "texture": "stars",
        "chart": {"primary": "#6366F1", "secondary": "#3B82F6", "accent": "#93C5FD",
                   "good": "#34D399", "warn": "#FBBF24", "bad": "#F87171",
                   "grid": "rgba(255,255,255,0.08)", "text": "#E4E4F4"},
    },
    "Light Academic": {
        "mode": "light",
        "primary": "#2563EB", "secondary": "#6366F1", "accent": "#0EA5E9",
        "gradient": "linear-gradient(135deg, #2563EB 0%, #6366F1 100%)",
        "glow": "rgba(37, 99, 235, 0.18)",
        "bg_base": "#F5F8FD", "bg_base2": "#EAF1FB",
        "surface": "rgba(255,255,255,0.60)", "surface_hover": "rgba(255,255,255,0.85)",
        "border": "rgba(15,23,42,0.10)",
        "text_primary": "#0F172A", "text_muted": "#5B6B85",
        "on_accent": "#FFFFFF",
        "blob1": "#93C5FD", "blob2": "#C7D2FE", "blob3": "#BFDBFE",
        "texture": "geo",
        "chart": {"primary": "#2563EB", "secondary": "#6366F1", "accent": "#0EA5E9",
                   "good": "#059669", "warn": "#D97706", "bad": "#DC2626",
                   "grid": "rgba(15,23,42,0.08)", "text": "#0F172A"},
    },
}
# "Auto" borrows Aurora's values as a safe default; inject_custom_css()
# additionally layers @media(prefers-color-scheme) overrides for it so
# the browser can swap toward Light Academic when the OS is in light mode.
THEMES["Auto"] = dict(THEMES["Aurora"])

THEME_NAMES = ["Aurora", "Ocean", "Emerald", "Sunset", "Midnight", "Light Academic", "Auto"]
THEME_ICONS = {
    "Aurora": "🟣", "Ocean": "🔵", "Emerald": "🟢", "Sunset": "🟠",
    "Midnight": "⚫", "Light Academic": "⚪", "Auto": "🌓",
}

# Kept for any external callers expecting the old name.
PALETTES = THEMES


def get_chart_colors(theme_name: str) -> dict:
    """
    Return the Plotly color set for the given theme, for use by
    interactive_charts.py. This changes ONLY colors — chart data,
    axes, and computed values are untouched by theming.
    """
    return THEMES.get(theme_name, THEMES["Aurora"])["chart"]


def _texture_layer(t: dict) -> dict:
    """
    Build ONE additional composable background-image layer for the
    theme's texture pattern (neural network / grid / stars / geometric
    lines). Returned as a dict of plain CSS value fragments — image,
    size, repeat — designed to be stacked as the 4th layer alongside
    the 3 blob gradients directly on [data-testid="stAppViewContainer"]
    (see inject_custom_css). "none" and "waves" contribute a fully
    transparent no-op layer; Sunset's "wave" motion instead comes from
    animating the base wash layer's position (see wave_shift below).
    """
    texture = t["texture"]
    noop = {"image": "linear-gradient(rgba(0,0,0,0), rgba(0,0,0,0))", "size": "10px 10px", "repeat": "no-repeat"}

    if texture == "network":
        svg = (
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E"
            "%3Cg fill='none' stroke='%2338BDF8' stroke-opacity='0.35' stroke-width='1'%3E"
            "%3Cline x1='20' y1='30' x2='90' y2='70'/%3E%3Cline x1='90' y1='70' x2='160' y2='40'/%3E"
            "%3Cline x1='90' y1='70' x2='110' y2='150'/%3E%3Cline x1='160' y1='40' x2='200' y2='120'/%3E"
            "%3Cline x1='30' y1='150' x2='110' y2='150'/%3E%3Cline x1='110' y1='150' x2='190' y2='180'/%3E"
            "%3C/g%3E%3Cg fill='%2367E8F9' fill-opacity='0.55'%3E"
            "%3Ccircle cx='20' cy='30' r='2.4'/%3E%3Ccircle cx='90' cy='70' r='2.6'/%3E"
            "%3Ccircle cx='160' cy='40' r='2.2'/%3E%3Ccircle cx='110' cy='150' r='2.6'/%3E"
            "%3Ccircle cx='200' cy='120' r='2.2'/%3E%3Ccircle cx='30' cy='150' r='2.2'/%3E"
            "%3Ccircle cx='190' cy='180' r='2.4'/%3E%3C/g%3E%3C/svg%3E"
        )
        return {"image": f'url("{svg}")', "size": "260px 260px", "repeat": "repeat"}
    if texture == "grid":
        svg = (
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='42' height='42'%3E"
            "%3Cpath d='M0 0.5H42M0.5 0V42' fill='none' stroke='%23A3E635' stroke-opacity='0.22' stroke-width='1'/%3E"
            "%3C/svg%3E"
        )
        return {"image": f'url("{svg}")', "size": "42px 42px", "repeat": "repeat"}
    if texture == "stars":
        svg = (
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E"
            "%3Cg fill='%23FFFFFF'%3E%3Ccircle cx='15' cy='40' r='1.2'/%3E%3Ccircle cx='80' cy='20' r='0.9'/%3E"
            "%3Ccircle cx='140' cy='90' r='1.4'/%3E%3Ccircle cx='200' cy='30' r='1'/%3E"
            "%3Ccircle cx='260' cy='70' r='1.2'/%3E%3Ccircle cx='40' cy='140' r='1'/%3E"
            "%3Ccircle cx='110' cy='170' r='1.3'/%3E%3Ccircle cx='180' cy='150' r='0.9'/%3E"
            "%3Ccircle cx='250' cy='190' r='1.2'/%3E%3Ccircle cx='30' cy='230' r='1'/%3E"
            "%3Ccircle cx='95' cy='250' r='1.3'/%3E%3Ccircle cx='170' cy='260' r='1'/%3E"
            "%3Ccircle cx='240' cy='240' r='1.2'/%3E%3Ccircle cx='280' cy='280' r='0.9'/%3E%3C/g%3E%3C/svg%3E"
        )
        return {"image": f'url("{svg}")', "size": "300px 300px", "repeat": "repeat"}
    if texture == "geo":
        svg = (
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E"
            "%3Cg fill='none' stroke='%232563EB' stroke-opacity='0.14' stroke-width='1'%3E"
            "%3Ccircle cx='80' cy='80' r='60'/%3E%3Ccircle cx='80' cy='80' r='30'/%3E"
            "%3Cpath d='M0 80 H160 M80 0 V160'/%3E%3C/g%3E%3C/svg%3E"
        )
        return {"image": f'url("{svg}")', "size": "160px 160px", "repeat": "repeat"}
    return noop  # "none" (Aurora) and "waves" (Sunset)


def inject_custom_css(theme_name: str = "Aurora"):
    """
    Inject the global custom CSS theme into the Streamlit app, including
    the animated background layer for the selected theme. Re-running this
    with a different theme_name is all that's needed to switch themes —
    no restart, no page reload.

    Args:
        theme_name: Key into THEMES.
    """
    t = THEMES.get(theme_name, THEMES["Aurora"])
    light = THEMES["Light Academic"]
    texture = _texture_layer(t)
    wave_shift = t.get("wave_shift", "0% 0%")
    light_wave_shift = light.get("wave_shift", "0% 0%")
    is_auto = theme_name == "Auto"
    # Native inputs need a more OPAQUE background than the glassy card
    # --surface value. On light themes, a semi-transparent white blended
    # over Streamlit's own (dark-by-default) input chrome reads as a
    # muddy gray box instead of a clean light one -- this fixes that.
    input_bg = "rgba(255,255,255,0.92)" if t.get("mode") == "light" else t["surface"]
    light_input_bg = "rgba(255,255,255,0.92)"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        :root {{
            --primary: {t['primary']};
            --secondary: {t['secondary']};
            --accent: {t['accent']};
            --gradient: {t['gradient']};
            --glow: {t['glow']};
            --bg-base: {t['bg_base']};
            --bg-base2: {t['bg_base2']};
            --surface: {t['surface']};
            --surface-hover: {t['surface_hover']};
            --border-soft: {t['border']};
            --text-primary: {t['text_primary']};
            --text-muted: {t['text_muted']};
            --on-accent: {t['on_accent']};
            --blob1: {t['blob1']};
            --blob2: {t['blob2']};
            --blob3: {t['blob3']};
            --wave-shift: {wave_shift};
            --input-bg: {input_bg};
        }}

        {"" if not is_auto else f'''
        @media (prefers-color-scheme: light) {{
            :root {{
                --primary: {light['primary']}; --secondary: {light['secondary']}; --accent: {light['accent']};
                --gradient: {light['gradient']}; --glow: {light['glow']};
                --bg-base: {light['bg_base']}; --bg-base2: {light['bg_base2']};
                --surface: {light['surface']}; --surface-hover: {light['surface_hover']};
                --border-soft: {light['border']}; --text-primary: {light['text_primary']};
                --text-muted: {light['text_muted']}; --on-accent: {light['on_accent']};
                --blob1: {light['blob1']}; --blob2: {light['blob2']}; --blob3: {light['blob3']};
                --wave-shift: {light_wave_shift};
                --input-bg: {light_input_bg};
            }}
        }}
        '''}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        h1, h2, h3, h4 {{
            font-family: 'Poppins', sans-serif !important;
            letter-spacing: -0.5px;
        }}

        /* ================= Global animated background =================
           Painted directly on Streamlit's own app container (NOT a
           position:fixed div injected via markdown) so it can't be
           clipped by any ancestor's overflow/scroll handling — a
           position:fixed layer nested deep in st.markdown() output is
           silently clipped by Streamlit's internal scroll container in
           some versions, which was the root cause of themes visually
           not applying. Painting as background-image directly on the
           testid Streamlit itself renders sidesteps that entirely. */
        [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-base) !important;
            background-image:
                radial-gradient(44vw 44vw at 10% -8%, var(--blob1) 0%, transparent 70%),
                radial-gradient(38vw 38vw at 92% 106%, var(--blob2) 0%, transparent 70%),
                radial-gradient(30vw 30vw at 84% 28%, var(--blob3) 0%, transparent 72%),
                {texture['image']},
                radial-gradient(120% 90% at 10% 0%, var(--bg-base2) 0%, var(--bg-base) 60%) !important;
            background-repeat: no-repeat, no-repeat, no-repeat, {texture['repeat']}, no-repeat;
            background-size: auto, auto, auto, {texture['size']}, cover;
            background-position: 10% -8%, 92% 106%, 84% 28%, 0 0, 0% 0%;
            background-attachment: fixed, fixed, fixed, fixed, fixed;
            animation: bgDrift 22s ease-in-out infinite !important;
            transition: background-color 0.6s ease;
        }}
        [data-testid="stHeader"], [data-testid="stMain"] {{
            background: transparent !important;
        }}
        @keyframes bgDrift {{
            0%   {{ background-position: 10% -8%, 92% 106%, 84% 28%, 0 0, 0% 0%; }}
            25%  {{ background-position: 26% 2%,  78% 90%,  66% 40%, 0 0, var(--wave-shift); }}
            50%  {{ background-position: 14% 14%, 90% 78%,  72% 18%, 0 0, 0% 0%; }}
            75%  {{ background-position: 30% -4%, 70% 100%, 60% 32%, 0 0, var(--wave-shift); }}
            100% {{ background-position: 10% -8%, 92% 106%, 84% 28%, 0 0, 0% 0%; }}
        }}
        .stApp {{ color: var(--text-primary) !important; }}
        .stApp, .stApp p, .stApp label, .stApp li,
        [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
        [data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"] p,
        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4,
        [data-testid="stHeadingWithActionElements"] * {{
            color: var(--text-primary) !important;
        }}
        [data-testid="stCaptionContainer"] {{ color: var(--text-muted) !important; }}
        hr {{ border-color: var(--border-soft) !important; }}

        /* ================= Sidebar ================= */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--bg-base2) 0%, var(--bg-base) 100%) !important;
            border-right: 1px solid var(--border-soft) !important;
            box-shadow: none !important;
        }}
        section[data-testid="stSidebar"] > div {{
            box-shadow: none !important;
            background: transparent !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stExpander"],
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border-soft) !important;
            border-radius: 14px !important;
        }}

        /* ================= Glassmorphic surfaces ================= */
        .glass-card, .step-card, .section-card, .hero-banner, .score-badge,
        div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--surface) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-soft) !important;
            border-radius: 20px !important;
            transition: transform 0.2s ease, box-shadow 0.25s ease, border-color 0.2s ease, background 0.2s ease;
        }}
        .glass-card:hover, .step-card:hover, div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-4px);
            border-color: var(--primary) !important;
            box-shadow: 0 14px 34px var(--glow);
            background: var(--surface-hover) !important;
        }}
        div[data-testid="stExpander"]:hover {{ border-color: var(--primary) !important; }}
        div[data-testid="stExpander"] summary {{ font-weight: 700 !important; font-family: 'Poppins', sans-serif !important; }}

        .glass-card {{ padding: 1.3rem 1.5rem; }}
        .glass-card .label {{
            font-size: 0.78rem; font-weight: 600; color: var(--text-muted);
            text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.4rem;
        }}
        .glass-card .value {{
            font-size: 2rem; font-weight: 800; font-family: 'Poppins', sans-serif;
            background: var(--gradient); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text;
        }}
        .glass-card .sub {{ font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem; }}
        .formula-row + .formula-row {{
            border-top: 1px solid var(--border-soft);
            margin-top: 0.6rem;
            padding-top: 0.6rem;
        }}
        .formula-row .formula-name {{
            font-size: 0.7rem; font-weight: 700; color: var(--text-muted);
            text-transform: uppercase; letter-spacing: 0.4px;
        }}
        .formula-row .formula-expr {{
            font-size: 0.72rem; color: var(--text-muted); opacity: 0.85;
            font-family: 'Inter', sans-serif; margin-top: 0.12rem;
        }}
        .formula-row .formula-value {{
            font-size: 1.35rem; font-weight: 800; font-family: 'Poppins', sans-serif;
            background: var(--gradient); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text;
            margin-top: 0.2rem;
        }}

        /* ================= Hero banner ================= */
        .hero-banner {{
            padding: 3rem 2.6rem;
            margin-bottom: 1.6rem;
            position: relative;
            overflow: hidden;
        }}
        .hero-title {{
            color: var(--text-primary);
            font-size: 2.6rem; font-weight: 800; margin: 0;
            letter-spacing: -1px; line-height: 1.12;
        }}
        .hero-title .accent-word {{
            background: var(--gradient); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text;
        }}
        .hero-subtitle {{
            color: var(--text-muted); font-size: 1.06rem; margin-top: 0.85rem;
            font-weight: 400; max-width: 680px; line-height: 1.55;
        }}
        .hero-cap {{
            position: absolute; top: 1.6rem; right: 2rem;
            width: 58px; height: 58px;
            animation: floatCap 6s ease-in-out infinite;
            filter: drop-shadow(0 0 14px var(--glow));
        }}
        @keyframes floatCap {{ 0%,100% {{ transform: translateY(0) rotate(-2deg); }} 50% {{ transform: translateY(-9px) rotate(2deg); }} }}
        .hero-particle {{
            position: absolute; border-radius: 50%; background: var(--accent);
            opacity: 0.5; filter: blur(1px); animation: floatParticle linear infinite;
        }}
        @keyframes floatParticle {{
            0%   {{ transform: translateY(0) translateX(0); opacity: 0; }}
            10%  {{ opacity: 0.55; }}
            90%  {{ opacity: 0.35; }}
            100% {{ transform: translateY(-70px) translateX(12px); opacity: 0; }}
        }}

        /* ================= Trust badge row + marquee ================= */
        .badge-row {{ display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1.4rem; }}
        .trust-chip {{
            display: inline-flex; align-items: center; gap: 0.4rem;
            background: var(--surface); border: 1px solid var(--border-soft);
            padding: 0.4rem 0.9rem; border-radius: 999px;
            font-size: 0.8rem; font-weight: 600; color: var(--text-primary);
        }}
        .eyebrow {{
            display: flex; align-items: center; gap: 0.5rem;
            font-size: 0.72rem; font-weight: 700; letter-spacing: 2.2px;
            text-transform: uppercase; color: var(--primary); margin-bottom: 0.6rem;
        }}
        .eyebrow::before {{ content: ""; width: 18px; height: 2px; background: var(--gradient); display: inline-block; }}
        .marquee-wrap {{
            overflow: hidden;
            -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
            mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
            border-top: 1px solid var(--border-soft); border-bottom: 1px solid var(--border-soft);
            padding: 0.9rem 0; margin-top: 1.3rem;
        }}
        .marquee-track {{ display: flex; width: max-content; gap: 2.4rem; animation: marquee 24s linear infinite; }}
        .marquee-wrap:hover .marquee-track {{ animation-play-state: paused; }}
        .marquee-item {{ display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; font-weight: 600; color: var(--text-muted); white-space: nowrap; }}
        @keyframes marquee {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}

        /* ================= Stat block + score badge ================= */
        .stat-block {{ padding: 0.5rem 0; }}
        .stat-block .stat-number {{ font-family: 'Poppins', sans-serif; font-size: 2.6rem; font-weight: 800; color: var(--text-primary); line-height: 1; }}
        .stat-block .stat-label {{ color: var(--text-muted); font-size: 0.85rem; margin-top: 0.35rem; font-weight: 500; }}
        .score-badge {{ display: inline-flex; align-items: baseline; gap: 0.45rem; padding: 1.1rem 1.5rem; }}
        .score-badge .score-value {{
            font-family: 'Poppins', sans-serif; font-size: 2.8rem; font-weight: 800;
            background: var(--gradient); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text; line-height: 1;
        }}
        .score-badge .score-max {{ font-size: 1rem; font-weight: 600; color: var(--text-muted); }}
        .score-badge-label {{ font-size: 0.78rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.55rem; }}

        /* ================= Step cards ================= */
        .step-card {{ padding: 1.5rem 1.6rem; height: 100%; }}
        .step-card:hover {{ transform: translateY(-3px); }}
        .step-card .step-number {{
            font-family: 'Poppins', sans-serif; font-size: 1.7rem; font-weight: 800;
            background: var(--gradient); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.45rem;
        }}
        .step-card .step-title {{ font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.02rem; color: var(--text-primary); margin-bottom: 0.4rem; }}
        .step-card .step-desc {{ color: var(--text-muted); font-size: 0.86rem; line-height: 1.5; }}

        .section-card {{ padding: 1.5rem 1.6rem; margin-bottom: 1.1rem; }}

        /* ================= Badges / chips ================= */
        .badge {{ display: inline-block; padding: 0.3rem 0.95rem; border-radius: 999px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.2px; }}
        .badge-success {{ background: rgba(52, 211, 153, 0.16); color: #34D399; }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.16); color: #F59E0B; }}
        .badge-danger  {{ background: rgba(239, 68, 68, 0.16);  color: #F87171; }}
        .badge-info    {{ background: rgba(59, 130, 246, 0.16); color: #60A5FA; }}
        .badge-purple  {{ background: rgba(139, 92, 246, 0.16); color: #A78BFA; }}

        /* ================= Buttons ================= */
        div.stButton > button, div.stDownloadButton > button {{
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-family: 'Poppins', sans-serif !important;
            border: 1px solid var(--border-soft) !important;
            transition: transform 0.16s ease, box-shadow 0.2s ease, background 0.2s ease !important;
        }}
        div.stButton > button[kind="primary"], div.stDownloadButton > button {{
            background: var(--gradient) !important;
            color: var(--on-accent) !important;
            border: none !important;
            box-shadow: 0 8px 22px var(--glow);
        }}
        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            transform: translateY(-2px) scale(1.015);
            box-shadow: 0 12px 28px var(--glow);
            border-color: var(--primary) !important;
        }}
        div.stButton > button:active, div.stDownloadButton > button:active {{ transform: translateY(0) scale(0.97); }}
        div.stButton > button:focus-visible, div.stDownloadButton > button:focus-visible,
        a:focus-visible, input:focus-visible, textarea:focus-visible {{
            outline: 2px solid var(--accent) !important;
            outline-offset: 2px !important;
        }}

        /* ================= Tabs ================= */
        .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
        .stTabs [data-baseweb="tab"] {{ border-radius: 10px 10px 0 0; padding: 10px 18px; font-weight: 600; font-family: 'Poppins', sans-serif; }}
        .stTabs [aria-selected="true"] {{ background: var(--gradient) !important; color: var(--on-accent) !important; }}

        /* ================= Native inputs (theme-aware) ================= */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-baseweb="select"] > div,
        [data-testid="stDataFrame"] {{
            background: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-soft) !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }}
        [data-testid="stTextInput"] > div, [data-testid="stNumberInput"] > div {{
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
        }}
        /* Browsers paint autofilled fields with their OWN background via an
           internal mechanism that ordinary background-color/!important can't
           reach (this is what made "University"/"Branch" render dark while
           identical fields like "Full Name" didn't — the browser recognized
           them as previously-saved values and autofilled its own styling).
           The inset-box-shadow trick is the standard, only reliable override. */
        [data-testid="stTextInput"] input:-webkit-autofill,
        [data-testid="stTextInput"] input:-webkit-autofill:hover,
        [data-testid="stTextInput"] input:-webkit-autofill:focus,
        [data-testid="stNumberInput"] input:-webkit-autofill,
        [data-testid="stNumberInput"] input:-webkit-autofill:hover,
        [data-testid="stNumberInput"] input:-webkit-autofill:focus {{
            -webkit-box-shadow: 0 0 0px 1000px var(--input-bg) inset !important;
            -webkit-text-fill-color: var(--text-primary) !important;
            caret-color: var(--text-primary) !important;
            transition: background-color 5000s ease-in-out 0s;
        }}
        [data-testid="stNumberInput"] button {{
            background: var(--input-bg) !important;
            border: 1px solid var(--border-soft) !important;
            box-shadow: none !important;
        }}
        [data-testid="stNumberInput"] button svg {{
            fill: var(--text-primary) !important;
        }}

        /* ================= Toggle / switch (theme-aware) =================
           st.toggle() had ZERO custom styling before this fix, so its
           track relied entirely on Streamlit's dark-base-theme-derived
           default colors. On Light Academic the UNCHECKED track color
           was close enough to the light background that it was nearly
           invisible at rest, and only became visible once BaseWeb's
           hover-only outline/border kicked in — exactly the reported
           "only visible on hover" bug. Multiple selector variants are
           targeted defensively (exact BaseWeb nesting can't be verified
           without a live browser), and hover is given the SAME explicit
           styling as the idle state so there is no visibility delta
           between them at all — the fix works whether or not any single
           selector below is the "real" one, since idle now always
           matches hover. */
        [data-testid="stCheckbox"], [data-testid="stToggle"] {{
            color: var(--text-primary) !important;
        }}
        [data-testid="stCheckbox"] div, [data-testid="stCheckbox"] span,
        [data-testid="stToggle"] div, [data-testid="stToggle"] span {{
            border-color: var(--border-soft) !important;
        }}
        [data-testid="stCheckbox"] [role="switch"],
        [data-testid="stToggle"] [role="switch"],
        [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div,
        [data-testid="stToggle"] [data-baseweb="checkbox"] > div,
        [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:hover,
        [data-testid="stToggle"] [data-baseweb="checkbox"] > div:hover,
        [data-testid="stCheckbox"] [role="switch"]:hover,
        [data-testid="stToggle"] [role="switch"]:hover {{
            background-color: var(--input-bg) !important;
            border: 1.5px solid var(--border-soft) !important;
            box-shadow: none !important;
        }}
        [data-testid="stCheckbox"] [role="switch"][aria-checked="true"],
        [data-testid="stToggle"] [role="switch"][aria-checked="true"],
        [data-testid="stCheckbox"] [aria-checked="true"] > div,
        [data-testid="stToggle"] [aria-checked="true"] > div {{
            background-color: var(--primary) !important;
            background-image: var(--gradient) !important;
            border-color: var(--primary) !important;
        }}
        [data-testid="stExpander"] summary, [data-testid="stExpander"] svg {{
            color: var(--text-primary) !important;
            fill: var(--text-primary) !important;
        }}

        /* ================= Dropdown / popover portals (theme-aware) =================
           BaseWeb renders the selectbox's OPEN dropdown list and st.popover's
           content in a portal appended near the end of <body>, not nested
           inside the widget's own DOM subtree — a plain descendant selector
           on the widget wouldn't reach it. CSS custom properties defined on
           :root still cascade to portal content since it's the same
           document, so these selectors work regardless of where in the DOM
           they land. Matters for the theme picker's own dropdown, and any
           future selectbox/popover. */
        [data-testid="stSelectboxVirtualDropdown"],
        [data-baseweb="popover"],
        [data-baseweb="menu"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border-soft) !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.18) !important;
        }}
        [data-testid="stSelectboxVirtualDropdown"] li,
        [data-baseweb="menu"] li,
        [data-baseweb="menu"] [role="option"] {{
            background: transparent !important;
            color: var(--text-primary) !important;
        }}
        [data-testid="stSelectboxVirtualDropdown"] li:hover,
        [data-baseweb="menu"] [role="option"]:hover {{
            background: var(--surface-hover) !important;
        }}
        [data-testid="stPopoverBody"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border-soft) !important;
            color: var(--text-primary) !important;
        }}

        /* ================= File uploader (theme-aware) ================= */
        [data-testid="stFileUploader"] section {{
            background: var(--surface) !important;
            border: 1px dashed var(--border-soft) !important;
            border-radius: 12px !important;
        }}
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section small {{
            color: var(--text-muted) !important;
        }}
        [data-testid="stFileUploader"] button {{
            background: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-soft) !important;
        }}

        /* ================= Status / spinner container (theme-aware) ================= */
        [data-testid="stStatusWidget"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border-soft) !important;
            border-radius: 14px !important;
        }}

        /* ================= Dataframe / data_editor (best-effort) =================
           The grid's CELL CONTENT is drawn on an HTML5 canvas (glide-data-
           grid), which CSS cannot recolor — it follows Streamlit's base
           theme from .streamlit/config.toml, not this dynamic per-theme
           CSS system. What CSS CAN reach is the container frame around
           that canvas, so it's given a themed border/radius rather than
           being left as an unstyled rectangle. */
        [data-testid="stDataFrame"], [data-testid="stDataFrameGlideDataEditor"] {{
            border: 1px solid var(--border-soft) !important;
            border-radius: 10px !important;
            overflow: hidden;
        }}

        /* ================= Progress bar (theme-aware) =================
           Scoped to [role="progressbar"] specifically — NOT a generic
           "> div > div" nesting guess — because the generic version also
           matched the text-caption element Streamlit renders alongside
           the bar (from st.progress(..., text=...)), painting it as a
           full-width gradient pill with the label sitting inside it,
           stacked on top of the real bar. role="progressbar" is the
           semantic ARIA role and can only match the actual bar. */
        [data-testid="stProgress"] [role="progressbar"] {{
            background-color: var(--border-soft) !important;
            border-radius: 999px !important;
        }}
        [data-testid="stProgress"] [role="progressbar"] > div {{
            background-color: var(--primary) !important;
            background-image: var(--gradient) !important;
            border-radius: 999px !important;
        }}

        /* ================= Grade pill ================= */
        .grade-pill {{
            display: inline-flex; align-items: center; justify-content: center;
            min-width: 46px; height: 28px; padding: 0 8px; border-radius: 8px;
            font-weight: 700; font-size: 0.85rem; color: var(--on-accent); background: var(--gradient);
        }}

        /* ================= Scrollbar ================= */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--primary); border-radius: 10px; opacity: 0.6; }}

        /* ================= Suggestion cards ================= */
        .suggestion-card {{
            display: flex; align-items: flex-start; gap: 0.7rem;
            background: var(--surface); border: 1px solid var(--border-soft);
            border-left: 3px solid var(--primary); border-radius: 12px;
            padding: 0.8rem 1.05rem; margin-bottom: 0.65rem;
            font-size: 0.93rem; color: var(--text-primary);
        }}

        .fade-in {{ animation: fadeIn 0.6s ease-in; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        @media (prefers-reduced-motion: reduce) {{
            [data-testid="stAppViewContainer"], .marquee-track, .hero-cap, .hero-particle,
            .fade-in, div.stButton > button, .glass-card, .step-card {{
                animation: none !important;
                transition: none !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Reusable HTML components
# --------------------------------------------------------------------------
_CAP_SVG = (
    '<svg class="hero-cap" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<defs><linearGradient id="capGrad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">'
    '<stop offset="0%" stop-color="var(--primary)"/>'
    '<stop offset="100%" stop-color="var(--secondary)"/>'
    '</linearGradient></defs>'
    '<path d="M32 10 L59 23 L32 36 L5 23 Z" fill="url(#capGrad)" opacity="0.92"/>'
    '<path d="M17 27 V41 Q32 49 47 41 V27" stroke="url(#capGrad)" stroke-width="2.4" '
    'fill="none" opacity="0.75" stroke-linecap="round"/>'
    '<circle cx="54" cy="26" r="2.2" fill="var(--accent)"/>'
    '<line x1="54" y1="26" x2="54" y2="44" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"/>'
    '<circle cx="54" cy="47" r="2.6" fill="var(--accent)"/>'
    '</svg>'
)


def _hero_particles(n: int = 6) -> str:
    """Generate a handful of small floating particle divs for the hero."""
    import random
    random.seed(7)  # deterministic layout across reruns
    spans = []
    for i in range(n):
        left = 8 + random.random() * 84
        size = 3 + random.random() * 4
        delay = round(random.random() * 8, 1)
        duration = 7 + round(random.random() * 6, 1)
        bottom = random.random() * 40
        spans.append(
            f'<span class="hero-particle" style="left:{left:.1f}%; bottom:{bottom:.0f}%; '
            f'width:{size:.1f}px; height:{size:.1f}px; '
            f'animation-duration:{duration}s; animation-delay:{delay}s;"></span>'
        )
    return "".join(spans)


def hero_banner(title: str, subtitle: str, accent_word: str = ""):
    """
    Render the top hero banner with an oversized heading, optional
    gradient-highlighted accent word, a small floating graduation-cap
    illustration, a handful of ambient particles, and a subtitle.

    IMPORTANT: this HTML is built as ONE flat string with no embedded
    newlines. Streamlit's markdown renderer treats a generic <div> as
    an HTML block that terminates at the first BLANK line — a single
    stray blank line (e.g. from interpolating a triple-quoted string
    that itself starts with "\\n") silently breaks the rest of the
    block out into escaped plain text instead of rendered HTML. Keeping
    everything on one line sidesteps that failure mode entirely.
    """
    display_title = title
    if accent_word and accent_word in title:
        display_title = title.replace(
            accent_word, f'<span class="accent-word">{accent_word}</span>'
        )
    html = (
        '<div class="hero-banner fade-in">'
        + _CAP_SVG
        + _hero_particles()
        + f'<div class="hero-title">{display_title}</div>'
        + f'<div class="hero-subtitle">{subtitle}</div>'
        + '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def badge_row(chips: list):
    """Render a horizontal row of small pill 'trust chips' (e.g. rating/stat highlights)."""
    chips_html = "".join(f'<span class="trust-chip">{c}</span>' for c in chips)
    st.markdown(f'<div class="badge-row fade-in">{chips_html}</div>', unsafe_allow_html=True)


def eyebrow(text: str):
    """Small tracked-out uppercase label above a section heading (editorial 'kicker')."""
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def marquee(chips: list):
    """Continuously auto-scrolling strip of small credential/trust chips (pauses on hover)."""
    items_html = "".join(f'<span class="marquee-item">{c}</span>' for c in chips)
    st.markdown(
        f'<div class="marquee-wrap fade-in"><div class="marquee-track">{items_html}{items_html}</div></div>',
        unsafe_allow_html=True,
    )


def score_badge(value: float, max_value: float = 10, label: str = "Current CGPA"):
    """Big 'Score X.XX / 10' style badge for a headline metric."""
    html = (
        f'<div class="score-badge-label">{label}</div>'
        '<div class="score-badge fade-in">'
        f'<span class="score-value">{value:.2f}</span>'
        f'<span class="score-max">/ {max_value:g}</span>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def percentage_formula_card(formulas: list, label: str = "Percentage"):
    """
    Compact card showing one or more CGPA -> Percentage formulas,
    stacked with a subtle divider between entries. Reuses the existing
    .glass-card/.label styling so it matches the other metric cards
    exactly rather than introducing a parallel visual style.

    Args:
        formulas: List of dicts, each {"name": str, "expr": str,
            "value": str}, e.g. {"name": "UGC Formula",
            "expr": "(CGPA − 0.75) × 10", "value": "76.40%"}.
        label: The card's overall label (small caps header).

    If a university supports only one formula in the future, pass a
    single-item list — the divider CSS (`.formula-row + .formula-row`)
    only activates between two-or-more rows, so a single formula
    renders cleanly with no divider and no code changes needed here.
    """
    rows = "".join(
        f'<div class="formula-row">'
        f'<div class="formula-name">{f["name"]}</div>'
        f'<div class="formula-expr">{f["expr"]}</div>'
        f'<div class="formula-value">{f["value"]}</div>'
        f'</div>'
        for f in formulas
    )
    html = f'<div class="glass-card fade-in"><div class="label">{label}</div>{rows}</div>'
    st.markdown(html, unsafe_allow_html=True)


def glass_metric(label: str, value: str, sub: str = ""):
    """Render a single glassmorphic metric card as an HTML block."""
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="glass-card fade-in"><div class="label">{label}</div>'
        f'<div class="value">{value}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def stat_block(number: str, label: str):
    """Render one big bold stat number with a caption underneath."""
    st.markdown(
        f'<div class="stat-block fade-in"><div class="stat-number">{number}</div>'
        f'<div class="stat-label">{label}</div></div>',
        unsafe_allow_html=True,
    )


def step_card(number: str, title: str, description: str):
    """Render one numbered step card for a 'how it works' process row."""
    st.markdown(
        f'<div class="step-card fade-in"><div class="step-number">{number}</div>'
        f'<div class="step-title">{title}</div><div class="step-desc">{description}</div></div>',
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str = "info") -> str:
    """Return an inline HTML badge/chip string. kind: success|warning|danger|info|purple."""
    return f'<span class="badge badge-{kind}">{text}</span>'


def suggestion_card(icon: str, text: str):
    """Render one AI-suggestion as a styled left-accented card."""
    st.markdown(
        f'<div class="suggestion-card"><div style="font-size:1.2rem;">{icon}</div><div>{text}</div></div>',
        unsafe_allow_html=True,
    )
