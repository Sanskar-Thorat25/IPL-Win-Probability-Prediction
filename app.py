
import base64
import math
import pickle
import re
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# IPL MATCHIQ - WIN PROBABILITY PREDICTOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


def _background_css(filename: str, fallback_url: str) -> str:
    """Embed the local stadium WEBP as a CSS data URL for deployment."""
    image_path = BASE_DIR / filename

    if image_path.is_file():
        try:
            encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
            return f'url("data:image/webp;base64,{encoded}")'
        except OSError:
            pass

    return f'url("{fallback_url}")'


DARK_STADIUM_BG = _background_css(
    "stadium_dark.webp",
    "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=2200&q=85",
)

LIGHT_STADIUM_BG = _background_css(
    "stadium_light.webp",
    "https://images.unsplash.com/photo-1521412644187-c49fa049e84d?auto=format&fit=crop&w=2200&q=85",
)


st.set_page_config(
    page_title="IPL Win Predictor | MatchIQ",
    layout="wide",
    initial_sidebar_state="collapsed",
)


TEAM_LOGOS = {
    "Chennai Super Kings": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F1622%2Ficon-light.svg",
    "Delhi Capitals": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F1396%2Ficon-light.svg",
    "Mumbai Indians": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F1854%2Ficon-light.svg",
    "Kolkata Knight Riders": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F1873%2Ficon-light.svg",
    "Rajasthan Royals": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F1558%2Ficon-light.svg",
    "Royal Challengers Bangalore": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F2138%2Ficon-light.svg",
    "Sunrisers Hyderabad": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F1153%2Ficon-light.svg",
    "Kings XI Punjab": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F2040%2Ficon-light.svg",
    "Gujarat Titans": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F2879%2Ficon-light.svg",
    "Lucknow Super Giants": "https://www.iplt20.com/api/team-assets?pathname=static%2Fteams%2F2880%2Ficon-light.svg",
}


TEAM_COLORS = {
    "Chennai Super Kings": "#F5B51B",
    "Delhi Capitals": "#2775D2",
    "Mumbai Indians": "#1687F8",
    "Kolkata Knight Riders": "#8B5CF6",
    "Rajasthan Royals": "#E65A9B",
    "Royal Challengers Bangalore": "#DC3A45",
    "Sunrisers Hyderabad": "#F07824",
    "Kings XI Punjab": "#D9474F",
    "Gujarat Titans": "#1D5C70",
    "Lucknow Super Giants": "#19A8C8",
}


TEAMS = [
    "Sunrisers Hyderabad",
    "Mumbai Indians",
    "Royal Challengers Bangalore",
    "Chennai Super Kings",
    "Rajasthan Royals",
    "Delhi Capitals",
    "Kolkata Knight Riders",
    "Kings XI Punjab",
]


CITIES = [
    "Hyderabad", "Bangalore", "Mumbai", "Indore", "Kolkata",
    "Delhi", "Chandigarh", "Jaipur", "Chennai", "Cape Town",
    "Port Elizabeth", "Durban", "Centurion", "East London",
    "Johannesburg", "Kimberley", "Bloemfontein", "Ahmedabad",
    "Cuttack", "Nagpur", "Dharamsala", "Visakhapatnam",
    "Pune", "Raipur", "Ranchi", "Abu Dhabi", "Sharjah",
    "Mohali", "Bengaluru",
]


VENUE_LABELS = {
    "Mumbai": "Wankhede Stadium, Mumbai",
    "Chennai": "M. A. Chidambaram Stadium, Chennai",
    "Kolkata": "Eden Gardens, Kolkata",
    "Delhi": "Arun Jaitley Stadium, Delhi",
    "Hyderabad": "Rajiv Gandhi Stadium, Hyderabad",
    "Bengaluru": "M. Chinnaswamy Stadium, Bengaluru",
    "Bangalore": "M. Chinnaswamy Stadium, Bangalore",
    "Ahmedabad": "Narendra Modi Stadium, Ahmedabad",
    "Jaipur": "Sawai Mansingh Stadium, Jaipur",
    "Mohali": "PCA Stadium, Mohali",
}


THEMES = {
    "dark": {
        "page": "#0B1120",
        "surface": "#111A2E",
        "surface2": "#0E1628",
        "border": "#1F2B47",
        "text": "#EEF2FA",
        "text2": "#B4BFD6",
        "muted": "#8794AF",
        "track": "#1D2842",
        "shadow": "0 12px 32px -14px rgba(0,0,0,.6)",
        "neutral": "#94A3B8",
        "warn_bg": "#2A2110",
        "warn_border": "#5B4716",
        "warn_text": "#F5D58A",
    },
    "light": {
        "page": "#F5F6FA",
        "surface": "#FFFFFF",
        "surface2": "#F8F9FC",
        "border": "#E3E7F0",
        "text": "#0E1730",
        "text2": "#3F4A63",
        "muted": "#667089",
        "track": "#E9ECF4",
        "shadow": "0 12px 32px -18px rgba(14,23,48,.16)",
        "neutral": "#475569",
        "warn_bg": "#FFFBEB",
        "warn_border": "#FDE68A",
        "warn_text": "#92400E",
    },
}


# ------------------------------------------------------------
# Session defaults (values persist across Streamlit reruns)
# ------------------------------------------------------------

st.session_state.setdefault("dark_mode", True)

# Every input starts empty. Clear returns the form to this state.
WIDGET_KEYS = [
    "batting_team",
    "bowling_team",
    "match_city",
    "target_score",
    "current_score",
    "overs_completed",
    "wickets_fallen",
]


def clear_all() -> None:
    """Empty every input so the placeholders show, and drop the old prediction."""
    for key in WIDGET_KEYS:
        st.session_state.pop(key, None)

    st.session_state.pop("prediction_result", None)


is_dark = bool(st.session_state["dark_mode"])
T = THEMES["dark" if is_dark else "light"]


# ============================================================
# HELPERS
# ============================================================

def flip_theme() -> None:
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]


def md(html: str) -> None:
    """Render HTML without Markdown treating indented lines as code."""
    st.markdown(
        re.sub(r"\s*\n\s*", " ", html.strip()),
        unsafe_allow_html=True,
    )


def hex_to_rgb(color: str):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def readable_text_on(color: str) -> str:
    r, g, b = hex_to_rgb(color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0E1730" if luminance > 0.62 else "#FFFFFF"


def color_distance(a: str, b: str) -> float:
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)

    return (
        (ra - rb) ** 2
        + (ga - gb) ** 2
        + (ba - bb) ** 2
    ) ** 0.5


def team_color(team: str) -> str:
    return TEAM_COLORS.get(team, "#4F7CFF")


def initials(team: str) -> str:
    return "".join(word[0] for word in team.split()[:3]).upper()


def logo_tile(team, size: int = 42, cls: str = "") -> str:
    """Show a trophy until a team is selected; then show its team logo."""
    if not team:
        return f"""
        <div class="logo-tile empty {cls}"
             style="width:{size}px;height:{size}px;"
             aria-label="Select a team">
            <svg viewBox="0 0 24 24" width="23" height="23"
                 fill="none" stroke="#D6A84F" stroke-width="1.6"
                 stroke-linecap="round" stroke-linejoin="round"
                 aria-hidden="true">
                <path d="M8 21h8M12 17v4M7 4h10"/>
                <path d="M5 4H3v4a4 4 0 0 0 4 4"/>
                <path d="M19 4h2v4a4 4 0 0 1-4 4"/>
                <path d="M5 4v5a7 7 0 0 0 14 0V4"/>
            </svg>
        </div>
        """

    src = escape(TEAM_LOGOS.get(team, ""), quote=True)

    return (
        f'<div class="logo-tile {cls}" style="width:{size}px;height:{size}px;">'
        f'<span>{escape(initials(team))}</span>'
        f'<img src="{src}" alt="{escape(team, quote=True)} logo">'
        f'</div>'
    )


def root_tokens(accent: str, on_accent: str) -> str:
    return (
        ":root{"
        f"--page:{T['page']};--surface:{T['surface']};--surface2:{T['surface2']};"
        f"--border:{T['border']};--text:{T['text']};--text2:{T['text2']};"
        f"--muted:{T['muted']};--track:{T['track']};--shadow:{T['shadow']};"
        f"--warn-bg:{T['warn_bg']};--warn-border:{T['warn_border']};"
        f"--warn-text:{T['warn_text']};"
        f"--accent:{accent};--accent-soft:{accent}33;--on-accent:{on_accent};"
        f"--stadium-bg:{DARK_STADIUM_BG if is_dark else LIGHT_STADIUM_BG};"
        f"--stadium-overlay:{'linear-gradient(180deg, rgba(3, 12, 25, .52), rgba(3, 12, 25, .83))' if is_dark else 'linear-gradient(180deg, rgba(246, 250, 255, .30), rgba(247, 250, 255, .78))'};"
        "--ease:cubic-bezier(.22,1,.36,1);"
        f"color-scheme:{'dark' if is_dark else 'light'};"
        "}"
    )


# Accent follows the selected batting team.
accent = team_color(st.session_state.get("batting_team") or "")
on_accent = readable_text_on(accent)


# ============================================================
# PAGE STYLES
# ============================================================

FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:"
    "wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');"
)


PAGE_CSS = r"""
html, body {
  background: var(--page) !important;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

/* Stadium image changes with the existing dark/light theme. */
.stApp {
  background-color: var(--page) !important;
  background-image: var(--stadium-overlay), var(--stadium-bg) !important;
  background-size: cover, cover !important;
  background-position: center top, center top !important;
  background-repeat: no-repeat, no-repeat !important;
  background-attachment: fixed, fixed !important;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

/* Let the stadium background remain visible behind the content. */
[data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], section.main, .main {
  background: transparent !important;
}

[data-testid="stMarkdownContainer"] {
  color: var(--text);
}

/* Keep Streamlit's fixed header from intercepting the theme-toggle clicks. */
[data-testid="stHeader"] {
  background: transparent !important;
  height: 0 !important;
  min-height: 0 !important;
  pointer-events: none !important;
  overflow: hidden;
}

[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stAppDeployButton"], #MainMenu, footer {
  visibility: hidden;
  display: none;
}

.block-container {
  max-width: 1240px;
  padding: 2.2rem 1.5rem 3rem;
}

.num {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-variant-numeric: tabular-nums;
}

/* ---------- Header ---------- */

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
}

.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 3px;
  padding: 9px 0;
  transition: background .4s var(--ease);
}

.brand-mark i {
  display: block;
  width: 4px;
  border-radius: 2px;
  background: var(--on-accent);
}

.brand-mark i:nth-child(1) { height: 8px; }
.brand-mark i:nth-child(2) { height: 13px; }
.brand-mark i:nth-child(3) { height: 18px; }

.brand-name {
  font-weight: 800;
  font-size: 1.12rem;
  letter-spacing: -.03em;
  line-height: 1.15;
}

.brand-sub {
  color: var(--muted);
  font-size: .78rem;
  margin-top: 2px;
}

[data-testid="stToggle"] p,
[data-testid="stCheckbox"] p {
  color: var(--muted) !important;
  font-size: .82rem;
  font-weight: 600;
}

/* ---------- Cards ---------- */

.st-key-inputs_card, .card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.st-key-inputs_card {
  padding: 1.25rem 1.3rem 1.3rem;
}

.card {
  padding: 1.35rem;
  margin-bottom: 1rem;
}

.card-title {
  font-weight: 800;
  font-size: 1rem;
  letter-spacing: -.02em;
}

.card-sub {
  color: var(--muted);
  font-size: .84rem;
  margin-top: .15rem;
  line-height: 1.5;
}

.section-label {
  color: var(--muted);
  font-size: .78rem;
  font-weight: 700;
  margin: .9rem 0 .15rem;
}

.rule {
  height: 1px;
  background: var(--border);
  margin: 1.1rem 0 .3rem;
}

/* ---------- Inputs ---------- */

label[data-testid="stWidgetLabel"] p {
  color: var(--text2) !important;
  font-size: .8rem !important;
  font-weight: 600 !important;
}

/* Select control */

div[data-baseweb="select"] > div {
  background-color: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  min-height: 42px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
}

div[data-baseweb="select"] div {
  background-color: transparent !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {
  color: var(--text) !important;
}

div[data-baseweb="select"] > div > div {
  padding-left: .15rem;
}

div[data-baseweb="select"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] [class*="singleValue"],
div[data-baseweb="select"] [class*="placeholder"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: .9rem !important;
  font-weight: 600 !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

div[data-baseweb="select"] svg {
  fill: var(--muted) !important;
  transition: transform .2s var(--ease);
}

div[data-baseweb="select"] > div:hover {
  border-color: var(--muted) !important;
}

div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="select"] > div[aria-expanded="true"] {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

/* Number inputs */

div[data-testid="stNumberInputContainer"] {
  background-color: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  min-height: 42px;
  overflow: hidden;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
}

div[data-testid="stNumberInputContainer"] div[data-baseweb="input"],
div[data-testid="stNumberInputContainer"] div[data-baseweb="base-input"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

div[data-testid="stNumberInputContainer"]:hover {
  border-color: var(--muted) !important;
}

div[data-testid="stNumberInputContainer"]:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

div[data-testid="stNumberInputContainer"] input {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: .88rem !important;
  font-weight: 600 !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  background: transparent !important;
}

[data-testid="stNumberInputStepUp"],
[data-testid="stNumberInputStepDown"] {
  background: transparent !important;
  color: var(--muted) !important;
}

[data-testid="stNumberInputStepUp"]:hover,
[data-testid="stNumberInputStepDown"]:hover {
  background: var(--track) !important;
  color: var(--text) !important;
}

/* Placeholders */

div[data-baseweb="select"] input::placeholder,
div[data-testid="stNumberInputContainer"] input::placeholder {
  color: var(--muted) !important;
  -webkit-text-fill-color: var(--muted) !important;
  opacity: .85 !important;
  font-weight: 500 !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}

div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="select"] [class*="placeholder"] * {
  color: var(--muted) !important;
  -webkit-text-fill-color: var(--muted) !important;
  font-weight: 500 !important;
}

.logo-tile.empty {
  background: var(--surface2);
  border: 1px dashed var(--border);
  border-radius: 11px;
  display: grid;
  place-items: center;
}

.logo-tile.empty svg {
  opacity: .9;
  transition: transform .2s ease, opacity .2s ease;
}

.logo-tile.empty:hover svg {
  transform: translateY(-2px);
  opacity: 1;
}

/* ---------- Dropdown list ---------- */

div[data-baseweb="popover"] {
  background: transparent !important;
  box-shadow: none !important;
}

div[data-baseweb="popover"] > div {
  background-color: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  box-shadow: 0 18px 40px -12px rgba(0,0,0,.35) !important;
  overflow: hidden;
  padding: 0;
}

div[data-baseweb="popover"] div[data-baseweb="menu"],
div[data-baseweb="popover"] ul[role="listbox"] {
  background-color: var(--surface) !important;
  padding: 6px !important;
  max-height: 320px;
}

div[data-baseweb="popover"] ul[role="listbox"] li {
  background-color: transparent !important;
  color: var(--text) !important;
  border-radius: 9px;
  margin: 1px 0;
  padding: .55rem .75rem !important;
  min-height: 0;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: .9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color .15s var(--ease);
}

div[data-baseweb="popover"] ul[role="listbox"] li * {
  background-color: transparent !important;
  color: inherit !important;
  font-family: inherit !important;
  font-size: inherit !important;
}

div[data-baseweb="popover"] ul[role="listbox"] li:hover,
div[data-baseweb="popover"] ul[role="listbox"] li[data-highlighted="true"] {
  background-color: var(--surface2) !important;
}

div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"] {
  background-color: var(--accent-soft) !important;
  font-weight: 700;
}

div[data-baseweb="popover"] ul[role="listbox"]::-webkit-scrollbar {
  width: 8px;
}

div[data-baseweb="popover"] ul[role="listbox"]::-webkit-scrollbar-thumb {
  background: var(--track);
  border-radius: 99px;
}

/* Team logo beside selectors */

.logo-tile {
  position: relative;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: 11px;
  overflow: hidden;
}

.logo-tile span {
  font-size: .72rem;
  font-weight: 800;
  color: #475569;
}

.logo-tile img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 5px;
  background: #FFFFFF;
}

.select-logo {
  margin-top: 1.7rem;
}

/* ---------- Buttons ---------- */

.stButton > button {
  min-height: 2.9rem;
  border-radius: 11px;
  font-weight: 700;
  font-size: .9rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: transform .2s var(--ease), box-shadow .2s var(--ease),
              filter .2s var(--ease), border-color .2s var(--ease);
}

.stButton > button:hover {
  transform: translateY(-1px);
}

.stButton > button:active {
  transform: translateY(0);
}

.stButton > button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--accent);
  border: 1px solid var(--accent);
  color: var(--on-accent);
  box-shadow: 0 8px 20px -10px var(--accent);
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--on-accent);
  filter: brightness(.93);
}

.stButton > button[kind="primary"] p,
.stButton > button[data-testid="stBaseButton-primary"] p {
  color: var(--on-accent) !important;
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover {
  border-color: var(--muted);
  color: var(--text);
}

.stButton > button[kind="secondary"] p,
.stButton > button[data-testid="stBaseButton-secondary"] p {
  color: inherit !important;
}

/* ---------- Chase card ---------- */

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: .7rem;
  margin-top: 1rem;
}

.stat {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: .8rem .9rem;
  transition: border-color .25s var(--ease), transform .25s var(--ease);
}

.stat:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.stat-label {
  color: var(--muted);
  font-size: .76rem;
  font-weight: 500;
}

.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.3rem;
  margin-top: .3rem;
}

.rate-row {
  margin-top: 1.1rem;
}

.rate-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: .82rem;
  color: var(--text2);
  font-weight: 600;
  margin-bottom: .4rem;
}

.rate-head .num {
  color: var(--text);
  font-size: .9rem;
}

.rate-track {
  height: 8px;
  border-radius: 99px;
  background: var(--track);
  overflow: hidden;
}

.rate-fill {
  height: 100%;
  border-radius: 99px;
  transition: width .8s var(--ease);
}

.rate-note {
  margin-top: 1rem;
  padding: .75rem .9rem;
  border-radius: 11px;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text2);
  font-size: .85rem;
  line-height: 1.5;
}

.prompt {
  border-style: dashed;
  box-shadow: none;
  background: transparent;
}

.stale {
  margin-bottom: 1rem;
  padding: .75rem 1rem;
  border-radius: 11px;
  font-size: .85rem;
  font-weight: 500;
  background: var(--warn-bg);
  border: 1px solid var(--warn-border);
  color: var(--warn-text);
}

.footer {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--muted);
  font-size: .76rem;
  margin-top: 1.4rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}

@media (max-width: 760px) {
  .block-container {
    padding: 1rem .8rem 2rem;
  }

  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .brand-sub {
    display: none;
  }
}
"""


RESULT_CSS = r"""
.enter { animation: rise .6s var(--ease) both; }
.verdict { font-size: 1.3rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.25; }
.snapshot { color: var(--muted); font-size: .86rem; margin-top: .3rem; line-height: 1.5; }
.matchup { display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; margin-top: 1.2rem; }
.panel { background: var(--surface2); border: 1px solid var(--border); border-radius: 14px; padding: 1rem .8rem .6rem; min-width: 0; }
.who { display: flex; align-items: center; gap: 10px; }
.tname { font-weight: 700; font-size: .92rem; line-height: 1.25; overflow-wrap: anywhere; }
.trole { color: var(--muted); font-size: .76rem; margin-top: 2px; }
.gauge { width: 100%; max-width: 270px; margin: .6rem auto 0; }
.gauge svg { display: block; width: 100%; height: auto; overflow: visible; }
.g-track { fill: none; stroke: var(--track); stroke-width: 10; stroke-linecap: round; }
.g-arc { fill: none; stroke-width: 10; stroke-linecap: round; animation: fill 1.4s var(--ease) both; }
.g-tick { stroke: var(--muted); opacity: .45; stroke-width: 1.2; stroke-linecap: round; }
.g-num { font-family: 'JetBrains Mono', monospace; font-size: 31px; font-weight: 700; fill: var(--text); letter-spacing: -1px; }
.g-num.empty { fill: var(--muted); }
.tname.empty { color: var(--muted); font-weight: 600; }
.g-cap { font-size: 10px; fill: var(--muted); font-weight: 500; }
.split { margin-top: 1.2rem; }
.split-labels { display: flex; justify-content: space-between; gap: 1rem; font-size: .82rem; font-weight: 600; color: var(--text2); margin-bottom: .45rem; }
.split-labels .num { color: var(--text); font-weight: 700; }
.split-bar { display: flex; height: 10px; border-radius: 99px; overflow: hidden; background: var(--track); gap: 3px; }
.seg { height: 100%; border-radius: 99px; transform-origin: left; animation: grow 1.2s var(--ease) both; }
.foot { color: var(--muted); font-size: .78rem; margin-top: 1.1rem; line-height: 1.5; }
@keyframes fill { from { stroke-dasharray: 0 100; } }
@keyframes grow { from { transform: scaleX(0); } }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 480px) { .matchup { grid-template-columns: 1fr; } }
"""


SUN_ICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    "stroke='%23111' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='4'/%3E"
    "%3Cpath d='M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'/%3E%3C/svg%3E"
)


MOON_ICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23fff'%3E"
    "%3Cpath d='M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7z'/%3E%3C/svg%3E"
)


def theme_toggle_css() -> str:
    """Pill switch: dark track + sun thumb on the left in light mode,
    white track + moon thumb on the right in dark mode."""

    if is_dark:
        track, border, thumb, left, icon = (
            "#FFFFFF",
            "#D5DBE8",
            "#000000",
            "calc(100% - 34px)",
            MOON_ICON,
        )
    else:
        track, border, thumb, left, icon = (
            "#2F3136",
            "#2F3136",
            "#FFFFFF",
            "4px",
            SUN_ICON,
        )

    return f"""
    .st-key-theme_toggle {{
      display: flex;
      justify-content: flex-end;
      position: relative;
      z-index: 1000001;
    }}

    .st-key-theme_toggle > div,
    .st-key-theme_toggle [data-testid="stButton"] {{
      width: 76px;
    }}

    .st-key-theme_toggle button {{
      position: relative;
      display: block;
      width: 76px;
      min-width: 76px;
      height: 40px;
      min-height: 40px;
      padding: 0;
      border-radius: 999px;
      overflow: hidden;
      cursor: pointer;
      background: {track};
      border: 1px solid {border};
      transition: background .3s var(--ease), border-color .3s var(--ease);
    }}

    .st-key-theme_toggle button:hover {{
      background: {track};
      border-color: var(--accent);
    }}

    .st-key-theme_toggle button:focus-visible {{
      outline: none;
      box-shadow: 0 0 0 3px var(--accent-soft);
    }}

    .st-key-theme_toggle button * {{
      font-size: 0 !important;
      line-height: 0 !important;
      color: transparent !important;
      pointer-events: none;
    }}

    .st-key-theme_toggle button::after {{
      content: "";
      position: absolute;
      top: 4px;
      left: {left};
      width: 30px;
      height: 30px;
      border-radius: 50%;
      pointer-events: none;
      background-color: {thumb};
      background-image: url("{icon}");
      background-repeat: no-repeat;
      background-position: center;
      background-size: 18px;
      box-shadow: 0 2px 6px rgba(0,0,0,.25);
      transition: left .3s var(--ease);
    }}
    """


st.markdown(
    f"<style>{FONT_IMPORT}{root_tokens(accent, on_accent)}{PAGE_CSS}{RESULT_CSS}{theme_toggle_css()}</style>",
    unsafe_allow_html=True,
)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():
    with open(BASE_DIR / "pipe.pkl", "rb") as model_file:
        return pickle.load(model_file)


try:
    pipe = load_model()
except FileNotFoundError:
    st.error("pipe.pkl was not found. Keep it beside app.py.")
    st.stop()
except Exception as exc:
    st.error(f"Could not load the model: {exc}")
    st.stop()


# ============================================================
# RESULT COMPONENT — GAUGES AND TEAM CARDS
# ============================================================

def gauge_svg(probability, color) -> str:
    """Draw a semicircular speedometer with tick marks."""

    cx, cy = 120, 120
    ticks = []

    for i in range(0, 11):
        angle = math.pi * (1 - i / 10)
        r_out = 76
        r_in = 69 if i % 5 == 0 else 72

        x1 = cx + r_in * math.cos(angle)
        y1 = cy - r_in * math.sin(angle)
        x2 = cx + r_out * math.cos(angle)
        y2 = cy - r_out * math.sin(angle)

        ticks.append(
            f'<line class="g-tick" x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )

    track_style = f' style="stroke:{color};opacity:.2"' if color else ""

    if probability is None:
        arc = ""
        number = (
            '<text x="120" y="106" text-anchor="middle" '
            'class="g-num empty">--</text>'
        )
        label = "Win probability not calculated yet"
    else:
        pct = max(0.0, min(100.0, probability * 100))

        arc = (
            f'<path class="g-arc" d="M 28 120 A 92 92 0 0 1 212 120" '
            f'pathLength="100" stroke="{color}" '
            f'style="stroke-dasharray:{pct:.2f} 100;"/>'
        )

        number = (
            f'<text x="120" y="106" text-anchor="middle" '
            f'class="g-num">{pct:.1f}%</text>'
        )
        label = f"Win probability {pct:.1f} percent"

    return f"""
    <div class="gauge">
      <svg viewBox="0 0 240 150" role="img" aria-label="{label}">
        <path class="g-track"
              d="M 28 120 A 92 92 0 0 1 212 120"
              pathLength="100"{track_style}/>
        {arc}
        {''.join(ticks)}
        {number}
        <text x="120" y="126" text-anchor="middle" class="g-cap">
          chance to win
        </text>
      </svg>
    </div>
    """


def panel_html(team, role: str, probability, color) -> str:
    name = (
        f'<div class="tname">{escape(team)}</div>'
        if team
        else f'<div class="tname empty">{escape(role)} team</div>'
    )

    return f"""
    <div class="panel">
      <div class="who">
        {logo_tile(team, 42)}
        <div style="min-width:0">
          {name}
          <div class="trole">{escape(role)}</div>
        </div>
      </div>
      {gauge_svg(probability, color)}
    </div>
    """


def build_matchup_html(result, live_bat, live_bowl) -> str:
    """Keep gauges visible before prediction; animate them after prediction."""

    if result:
        bat, bowl = result["batting_team"], result["bowling_team"]
        bat_p = result["batting_probability"]
        bowl_p = result["bowling_probability"]
    else:
        bat, bowl, bat_p, bowl_p = live_bat, live_bowl, None, None

    bat_color = team_color(bat) if bat else None
    bowl_color = team_color(bowl) if bowl else None

    if bat_color and bowl_color and color_distance(bat_color, bowl_color) < 70:
        bowl_color = T["neutral"]

    if result:
        gap = bat_p - bowl_p
        leader = bat if gap >= 0 else bowl
        size = abs(gap)

        if size < 0.10:
            verdict = "Too close to call"
        elif size < 0.25:
            verdict = f"{escape(leader)} have a slight edge"
        elif size < 0.45:
            verdict = f"{escape(leader)} have a clear edge"
        else:
            verdict = f"{escape(leader)} are strong favourites"

        venue = VENUE_LABELS.get(result["city"], result["city"])

        snapshot = (
            f"{escape(bat)} are chasing {result['target']} and are "
            f"{result['score']}/{result['wickets']} after "
            f"{result['overs']:.1f} overs at {escape(venue)}."
        )

    elif bat and bowl:
        verdict = f"{escape(bat)} vs {escape(bowl)}"
        snapshot = (
            "Enter the score and select Calculate win probability "
            "to fill the gauges."
        )

    elif bat or bowl:
        verdict = "Choose the other team"
        snapshot = (
            "Each gauge takes its team's colour as soon as the team is selected."
        )

    else:
        verdict = "Pick the teams to begin"
        snapshot = (
            "Select the batting and bowling teams, then enter the current score."
        )

    if result:
        split_labels = (
            f'<span>{escape(bat)} '
            f'<span class="num">{bat_p * 100:.1f}%</span></span>'
            f'<span><span class="num">{bowl_p * 100:.1f}%</span> '
            f'{escape(bowl)}</span>'
        )

        split_bar = (
            f'<div class="seg" style="width:{bat_p * 100:.2f}%;'
            f'background:{bat_color};"></div>'
            f'<div class="seg" style="width:{bowl_p * 100:.2f}%;'
            f'background:{bowl_color};"></div>'
        )

    else:
        split_labels = (
            f'<span>{escape(bat) if bat else "Batting team"}</span>'
            f'<span>{escape(bowl) if bowl else "Bowling team"}</span>'
        )
        split_bar = ""

    return f"""
    <section class="card enter">
      <div class="verdict">{verdict}</div>
      <div class="snapshot">{snapshot}</div>

      <div class="matchup">
        {panel_html(bat, "Batting", bat_p, bat_color)}
        {panel_html(bowl, "Bowling", bowl_p, bowl_color)}
      </div>

      <div class="split">
        <div class="split-labels">{split_labels}</div>
        <div class="split-bar">{split_bar}</div>
      </div>

      <div class="foot">
        Model estimates based on historical IPL data.
        They are not guaranteed outcomes.
      </div>
    </section>
    """


def rate_row_html(label: str, value: float, scale: float, color: str) -> str:
    width = (
        max(0.0, min(100.0, (value / scale) * 100))
        if scale > 0
        else 0
    )

    return f"""
    <div class="rate-row">
      <div class="rate-head">
        <span>{label}</span>
        <span class="num">{value:.2f}</span>
      </div>
      <div class="rate-track">
        <div class="rate-fill"
             style="width:{width:.1f}%;background:{color};"></div>
      </div>
    </div>
    """


# ============================================================
# HEADER
# ============================================================

head_col, theme_col = st.columns(
    [5, 1],
    gap="small",
    vertical_alignment="center",
)

with head_col:
    md("""
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">
        <i></i><i></i><i></i>
      </div>
      <div>
        <div class="brand-name">IPL Win Predictor</div>
        <div class="brand-sub">Second-innings chase analysis</div>
      </div>
    </div>
    """)

with theme_col:
    st.button(
        "Switch theme",
        key="theme_toggle",
        on_click=flip_theme,
    )

st.markdown(
    "<div style='height:.9rem'></div>",
    unsafe_allow_html=True,
)


# ============================================================
# MAIN LAYOUT
# ============================================================

input_col, result_col = st.columns([0.85, 1.6], gap="large")


# ============================================================
# INPUTS
# ============================================================

with input_col:
    with st.container(key="inputs_card"):
        md('<div class="card-title">Match inputs</div>')
        md('<div class="section-label">Teams and venue</div>')

        logo_col, select_col = st.columns([0.2, 0.8], gap="small")

        with logo_col:
            md(
                logo_tile(
                    st.session_state.get("batting_team"),
                    42,
                    "select-logo",
                )
            )

        with select_col:
            batting_team = st.selectbox(
                "Batting team",
                TEAMS,
                index=None,
                placeholder="Select batting team",
                key="batting_team",
            )

        bowling_options = [t for t in TEAMS if t != batting_team]

        # Drop a stale choice if the batting team was just changed to match it.
        if st.session_state.get("bowling_team") not in bowling_options + [None]:
            st.session_state.pop("bowling_team", None)

        logo_col, select_col = st.columns([0.2, 0.8], gap="small")

        with logo_col:
            md(
                logo_tile(
                    st.session_state.get("bowling_team"),
                    42,
                    "select-logo",
                )
            )

        with select_col:
            bowling_team = st.selectbox(
                "Bowling team",
                bowling_options,
                index=None,
                placeholder="Select bowling team",
                key="bowling_team",
            )

        cities_sorted = sorted(CITIES)

        selected_city = st.selectbox(
            "Venue",
            cities_sorted,
            index=None,
            format_func=lambda city: VENUE_LABELS.get(city, city),
            placeholder="Select venue",
            key="match_city",
        )

        md(
            '<div class="rule"></div>'
            '<div class="section-label" style="margin-top:.6rem">'
            'Current score</div>'
        )

        def number_field(label, placeholder, **kwargs):
            """Use number_input placeholders when supported by this Streamlit version."""
            try:
                return st.number_input(
                    label,
                    placeholder=placeholder,
                    **kwargs,
                )
            except TypeError:
                return st.number_input(label, **kwargs)

        target_col, score_col = st.columns(2, gap="small")

        with target_col:
            target = number_field(
                "Target",
                "Target",
                min_value=1,
                max_value=1000,
                step=1,
                value=None,
                key="target_score",
            )

        with score_col:
            score = number_field(
                "Score",
                "Score",
                min_value=0,
                max_value=1000,
                step=1,
                value=None,
                key="current_score",
            )

        overs_col, wickets_col = st.columns(2, gap="small")

        with overs_col:
            overs = number_field(
                "Overs completed",
                "Overs",
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                format="%.1f",
                value=None,
                key="overs_completed",
            )

        with wickets_col:
            wickets = number_field(
                "Wickets fallen",
                "Wickets",
                min_value=0,
                max_value=10,
                step=1,
                value=None,
                key="wickets_fallen",
            )

        st.markdown(
            "<div style='height:.4rem'></div>",
            unsafe_allow_html=True,
        )

        calc_col, clear_col = st.columns([2, 1], gap="small")

        with calc_col:
            predict_clicked = st.button(
                "Calculate win probability",
                type="primary",
                use_container_width=True,
                key="calculate_prediction",
            )

        with clear_col:
            st.button(
                "Clear",
                use_container_width=True,
                key="clear_prediction",
                on_click=clear_all,
            )


# ============================================================
# MATCH CALCULATIONS (unchanged)
# ============================================================

numbers_ready = None not in (target, score, overs, wickets)

inputs_ready = (
    numbers_ready
    and None not in (batting_team, bowling_team, selected_city)
)

if numbers_ready:
    runs_left = target - score
    balls_left = max(0, 120 - (overs * 6))
    wickets_left = 10 - wickets
    crr = score / overs if overs > 0 else 0
    rrr = (runs_left * 6 / balls_left) if balls_left > 0 else 0
else:
    runs_left = balls_left = wickets_left = crr = rrr = 0

input_signature = (
    batting_team,
    bowling_team,
    selected_city,
    target,
    score,
    overs,
    wickets,
)


# ============================================================
# PREDICTION (original nine features preserved)
# ============================================================

if predict_clicked:
    error_message = None

    if not inputs_ready:
        error_message = "Fill in every field before calculating."
    elif batting_team == bowling_team:
        error_message = "Choose two different teams."
    elif overs <= 0:
        error_message = "Overs completed must be greater than zero."
    elif overs >= 20:
        error_message = "The 20-over innings is complete."
    elif wickets >= 10:
        error_message = "All wickets have fallen."
    elif score >= target:
        error_message = "The target has already been reached."
    elif runs_left < 0:
        error_message = "Current score cannot exceed the target."

    if error_message:
        st.session_state.pop("prediction_result", None)

        with result_col:
            st.error(error_message)

    else:
        model_input = pd.DataFrame({
            "batting_team": [batting_team],
            "bowling_team": [bowling_team],
            "city": [selected_city],
            "runs_left": [runs_left],
            "balls_left": [balls_left],
            "wickets_left": [wickets_left],
            "total_runs_x": [target],
            "crr": [crr],
            "rrr": [rrr],
        })

        try:
            with st.spinner("Calculating match probabilities..."):
                probabilities = pipe.predict_proba(model_input)[0]

            st.session_state["prediction_result"] = {
                "batting_team": batting_team,
                "bowling_team": bowling_team,
                "batting_probability": float(probabilities[1]),
                "bowling_probability": float(probabilities[0]),
                "runs_left": max(0, runs_left),
                "balls_left": int(round(balls_left)),
                "wickets_left": wickets_left,
                "target": target,
                "score": score,
                "overs": overs,
                "wickets": wickets,
                "city": selected_city,
                "signature": input_signature,
            }

        except Exception as exc:
            with result_col:
                st.error(f"Prediction failed: {exc}")


# ============================================================
# RESULTS
# ============================================================

with result_col:
    result = st.session_state.get("prediction_result")
    notice_slot = st.empty()

    if result is not None and result.get("signature") != input_signature:
        notice_slot.markdown(
            '<div class="stale">The inputs have changed since this prediction. '
            'Select Calculate win probability to update it.</div>',
            unsafe_allow_html=True,
        )

    md(build_matchup_html(result, batting_team, bowling_team))

    # ---------- Live chase situation ----------

    if numbers_ready:
        live_runs = max(0, runs_left)
        live_balls = int(round(balls_left))
        scale = max(crr, rrr, 1.0) * 1.15

        if live_runs == 0:
            note = "The target has been reached."
        elif live_balls == 0:
            note = "No balls remain in the innings."
        elif overs <= 0:
            note = (
                f"{live_runs} runs are needed from {live_balls} balls. "
                "Enter overs completed to compare run rates."
            )
        else:
            diff = rrr - crr

            if diff > 0.05:
                note = (
                    f"The chase needs {diff:.2f} more runs per over "
                    "than the current scoring rate."
                )
            elif diff < -0.05:
                note = (
                    f"The chase is scoring {abs(diff):.2f} runs per over "
                    "faster than the rate required."
                )
            else:
                note = "The current rate matches the rate required."

        required_color = T["muted"] if rrr <= crr else T["text"]

        md(f"""
        <div class="card">
          <div class="card-title">Chase situation</div>
          <div class="card-sub">Updates live as you change the score.</div>

          <div class="stat-grid">
            <div class="stat">
              <div class="stat-label">Score</div>
              <div class="stat-value">{score}/{wickets}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Runs required</div>
              <div class="stat-value">{live_runs}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Balls remaining</div>
              <div class="stat-value">{live_balls}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Wickets in hand</div>
              <div class="stat-value">{wickets_left}</div>
            </div>
          </div>

          {rate_row_html("Current run rate", crr, scale, accent)}
          {rate_row_html("Required run rate", rrr, scale, required_color)}

          <div class="rate-note">{note}</div>
        </div>
        """)

    else:
        md("""
        <div class="card prompt">
          <div class="card-title">Chase situation</div>
          <div class="card-sub">
            Enter the target, score, overs and wickets to see the live chase.
          </div>
        </div>
        """)


# ============================================================
# FOOTER
# ============================================================

md("""
<div class="footer">
  <span>Machine-learning estimates, not guaranteed outcomes</span>
</div>
""")
