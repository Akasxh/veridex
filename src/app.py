"""Veridex — Multi-page Streamlit web interface."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

import os

import plotly.graph_objects as go
import streamlit as st

try:
    from src.agent import ResearchAgent, ResearchResult, create_search_engine
    from src.demo import get_demo_queries, get_demo_result
    from src.report import ReportGenerator
except ImportError:
    from agent import ResearchAgent, ResearchResult, create_search_engine  # type: ignore[no-redef]
    from demo import get_demo_queries, get_demo_result  # type: ignore[no-redef]
    from report import ReportGenerator  # type: ignore[no-redef]

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Veridex - AI Web Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Veridex - Autonomous web research with NLP. No API keys required.",
    },
)

# ---------------------------------------------------------------------------
# Plotly shared layout
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT: dict[str, Any] = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#8e8ea0", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="#1e1e2e", zerolinecolor="#1e1e2e"),
    yaxis=dict(gridcolor="#1e1e2e", zerolinecolor="#1e1e2e"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8e8ea0")),
    hoverlabel=dict(bgcolor="#1a1a28", font_size=12, font_family="Inter"),
)
CHART_COLORS = ["#6c63ff", "#a855f7", "#22c55e", "#eab308", "#ef4444", "#3b82f6"]

STOPWORDS = frozenset(
    "the a an of in on and or for to is it how what why with from by this that are was were "
    "be been has have had do does did will would could should may might can shall not no its".split()
)

# ---------------------------------------------------------------------------
# CSS injection (PIXEL design system)
# ---------------------------------------------------------------------------


def inject_css() -> None:
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-tertiary: #1a1a28;
    --bg-sidebar: #0d0d14;
    --border-primary: #1e1e2e;
    --border-hover: #2a2a3e;
    --text-primary: #ececf1;
    --text-secondary: #8e8ea0;
    --text-tertiary: #565869;
    --accent-primary: #6c63ff;
    --accent-primary-hover: #7b73ff;
    --accent-secondary: #a855f7;
    --success: #22c55e;
    --success-bg: rgba(34,197,94,0.1);
    --warning: #eab308;
    --warning-bg: rgba(234,179,8,0.1);
    --danger: #ef4444;
    --danger-bg: rgba(239,68,68,0.1);
    --info: #3b82f6;
    --info-bg: rgba(59,130,246,0.1);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 20px;
    --radius-full: 9999px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 20px rgba(108,99,255,0.15);
}
html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-primary) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stMultiSelect label {
    color: var(--text-secondary) !important;
    font-weight: 500;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 2px !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 10px 16px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: var(--text-secondary) !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:hover {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label[data-checked="true"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: rgba(108,99,255,0.12) !important;
    color: var(--accent-primary) !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-glow) !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label > div:first-child {
    display: none !important;
}
div[data-testid="stMetric"] {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px 24px !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stMetric"]:hover {
    border-color: var(--accent-primary) !important;
    box-shadow: var(--shadow-glow) !important;
}
div[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #6c63ff 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    margin-top: 8px;
    line-height: 1.6;
    max-width: 640px;
}
.feature-tag {
    display: inline-block;
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 5px 14px;
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    margin: 3px 4px;
    font-weight: 500;
    border: 1px solid var(--border-primary);
    transition: all 0.15s ease;
}
.feature-tag:hover {
    border-color: var(--accent-primary);
    color: var(--text-primary);
}
.cred-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.cred-badge--high { background: var(--success-bg); color: var(--success); border: 1px solid var(--success); }
.cred-badge--medium { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning); }
.cred-badge--low { background: var(--danger-bg); color: var(--danger); border: 1px solid var(--danger); }
.source-card {
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    padding: 18px 22px;
    margin: 10px 0;
    border: 1px solid var(--border-primary);
    border-left-width: 4px;
    border-left-color: var(--accent-primary);
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}
.source-card:hover { border-color: var(--border-hover); box-shadow: var(--shadow-md); transform: translateY(-1px); }
.source-card--high { border-left-color: var(--success) !important; }
.source-card--medium { border-left-color: var(--warning) !important; }
.source-card--low { border-left-color: var(--danger) !important; }
.source-card__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.source-card__title { color: var(--text-primary) !important; text-decoration: none !important; font-weight: 600; font-size: 0.95rem; flex: 1; margin-right: 12px; }
.source-card__title:hover { color: var(--accent-primary) !important; }
.source-card__meta { display: flex; gap: 16px; color: var(--text-tertiary); font-size: 0.8rem; margin-bottom: 6px; }
.source-card__snippet { color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5; margin: 6px 0 0 0; }
.stat-card {
    background: var(--info-bg);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin: 8px 0;
    border-left: 3px solid var(--info);
    font-size: 0.9rem;
    color: var(--text-primary);
    line-height: 1.5;
}
.metric-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-left: 4px solid var(--accent-primary);
    border-radius: var(--radius-lg);
    padding: 20px 24px;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}
.metric-card:hover { border-color: var(--border-hover); box-shadow: var(--shadow-glow); }
.metric-card--success { border-left-color: var(--success); }
.metric-card--warning { border-left-color: var(--warning); }
.metric-card--danger { border-left-color: var(--danger); }
.metric-label {
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}
.metric-value {
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
}
.step-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 24px 20px;
    text-align: center;
    transition: all 0.2s ease;
    height: 100%;
}
.step-card:hover { border-color: var(--accent-primary); box-shadow: var(--shadow-glow); transform: translateY(-2px); }
.step-card__number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    background: linear-gradient(135deg, #6c63ff, #a855f7);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 12px;
}
.step-card__icon { font-size: 2rem; margin-bottom: 10px; }
.step-card__title { color: var(--text-primary); font-weight: 600; font-size: 1rem; margin-bottom: 8px; }
.step-card__desc { color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5; }
.empty-state { text-align: center; padding: 60px 20px; }
.empty-state__icon { font-size: 3rem; margin-bottom: 16px; opacity: 0.4; }
.empty-state__title { color: var(--text-secondary); font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
.empty-state__desc { color: var(--text-tertiary); font-size: 0.9rem; max-width: 400px; margin: 0 auto; line-height: 1.5; }
.demo-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 20px;
    transition: all 0.2s ease;
    height: 100%;
}
.demo-card:hover { border-color: var(--accent-primary); box-shadow: var(--shadow-glow); }
.demo-card__title { color: var(--text-primary); font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; }
.demo-card__desc { color: var(--text-secondary); font-size: 0.83rem; line-height: 1.5; }
.consensus-card {
    background: var(--success-bg);
    border: 1px solid var(--success);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin: 8px 0;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.5;
}
.conflict-card {
    background: var(--danger-bg);
    border: 1px solid var(--danger);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin: 8px 0;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.5;
}
.summary-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 24px;
    margin: 16px 0;
    line-height: 1.7;
    color: var(--text-primary);
    font-size: 0.925rem;
}
.entity-pill {
    display: inline-block;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    margin: 3px;
    border: 1px solid var(--border-primary);
}
.finding-row {
    background: var(--bg-secondary);
    border-left: 3px solid var(--accent-primary);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 14px 18px;
    margin: 8px 0;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.6;
}
.finding-row__number { color: var(--accent-primary); font-family: 'JetBrains Mono', monospace; font-weight: 700; margin-right: 10px; }
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: var(--bg-secondary) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    border: 1px solid var(--border-primary) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent-primary) !important; }
.stTextInput > div > div > input {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    padding: 12px 16px !important;
    font-size: 0.925rem !important;
}
.stTextInput > div > div > input:focus { border-color: var(--accent-primary) !important; box-shadow: var(--shadow-glow) !important; }
.stTextInput > div > div > input::placeholder { color: var(--text-tertiary) !important; }
.stButton > button {
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 8px 20px !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border-primary) !important;
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}
.stButton > button:hover { border-color: var(--accent-primary) !important; box-shadow: var(--shadow-glow) !important; }
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #6c63ff 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    opacity: 0.9 !important;
    box-shadow: 0 4px 15px rgba(108,99,255,0.4) !important;
}
.stDownloadButton > button {
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-primary) !important;
    color: var(--text-primary) !important;
}
.stDownloadButton > button:hover { border-color: var(--accent-primary) !important; }
.streamlit-expanderHeader {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-primary) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
}
.stSelectbox > div > div { background: var(--bg-secondary) !important; border: 1px solid var(--border-primary) !important; border-radius: var(--radius-md) !important; color: var(--text-primary) !important; }
.stSlider > div > div > div > div { background: var(--accent-primary) !important; }
hr { border-color: var(--border-primary) !important; }
/* scrollbar styles moved to Motion & Polish section below */
.sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 8px 0 20px 0; border-bottom: 1px solid var(--border-primary); margin-bottom: 16px; }
.sidebar-brand__icon { font-size: 1.5rem; }
.sidebar-brand__text { font-size: 1.1rem; font-weight: 700; color: var(--text-primary) !important; }
.sidebar-brand__version { font-size: 0.65rem; font-weight: 500; color: var(--text-tertiary) !important; background: var(--bg-tertiary); padding: 2px 8px; border-radius: var(--radius-full); }
.sidebar-footer { font-size: 0.72rem; color: var(--text-tertiary) !important; text-align: center; border-top: 1px solid var(--border-primary); padding-top: 12px; margin-top: 24px; }
.stAlert > div { border-radius: var(--radius-md) !important; font-size: 0.875rem !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, #6c63ff, #a855f7) !important; border-radius: var(--radius-full) !important; }
.arch-node { display: inline-flex; align-items: center; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); padding: 10px 16px; font-size: 0.8rem; font-weight: 500; color: var(--text-primary); }
.arch-arrow { color: var(--accent-primary); font-size: 1.2rem; margin: 0 8px; }

/* ---- Motion & Polish (LUMEN) ---- */

/* Card hover lift */
.source-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.source-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }

/* Metric card hover */
div[data-testid="stMetric"] { transition: transform 0.2s ease, box-shadow 0.2s ease; }
div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }

/* Fade-in-up keyframe */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.stMarkdown, div[data-testid="stMetric"], .stPlotlyChart {
  animation: fadeInUp 0.4s ease-out;
}

/* Button press effect */
.stButton button:active { transform: scale(0.97); }

/* Smooth tab panel transitions */
.stTabs [data-baseweb="tab-panel"] { animation: fadeInUp 0.3s ease-out; }

/* Progress bar glow */
.stProgress > div > div {
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
  transition: width 0.3s ease;
}

/* Sidebar radio hover */
section[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  transition: background 0.2s ease;
}

/* Expander animation */
.streamlit-expanderHeader { transition: background 0.2s ease; }
.streamlit-expanderHeader:hover { background: rgba(102, 126, 234, 0.1) !important; }

/* Upgraded scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(102, 126, 234, 0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(102, 126, 234, 0.5); }

/* Staggered source card animation */
.source-card { animation: fadeInUp 0.4s ease-out both; }
.source-card:nth-child(1) { animation-delay: 0s; }
.source-card:nth-child(2) { animation-delay: 0.05s; }
.source-card:nth-child(3) { animation-delay: 0.05s; }
.source-card:nth-child(4) { animation-delay: 0.1s; }
.source-card:nth-child(5) { animation-delay: 0.15s; }
.source-card:nth-child(6) { animation-delay: 0.2s; }
.source-card:nth-child(7) { animation-delay: 0.25s; }

/* Empty state fade-in */
.empty-state { animation: fadeInUp 0.5s ease-out; }

/* Step cards stagger */
.step-card { animation: fadeInUp 0.4s ease-out both; }

/* Demo cards stagger */
.demo-card { animation: fadeInUp 0.4s ease-out both; }

/* Finding rows stagger */
.finding-row { animation: fadeInUp 0.35s ease-out both; }

/* Stat / consensus / conflict card entrance */
.stat-card, .consensus-card, .conflict-card { animation: fadeInUp 0.4s ease-out; }

/* Summary container entrance */
.summary-container { animation: fadeInUp 0.5s ease-out; }

/* Entity pill hover */
.entity-pill { transition: background 0.15s ease, border-color 0.15s ease; }
.entity-pill:hover { background: rgba(108,99,255,0.15); border-color: var(--accent-primary); }

/* Feature tag hover lift */
.feature-tag { transition: all 0.15s ease, transform 0.15s ease; }
.feature-tag:hover { transform: translateY(-1px); }
</style>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Cached agent
# ---------------------------------------------------------------------------


@st.cache_resource
def get_agent(provider: str = "duckduckgo") -> ResearchAgent:
    return ResearchAgent(search_engine=create_search_engine(provider))


# ---------------------------------------------------------------------------
# Reusable HTML helpers
# ---------------------------------------------------------------------------


def render_cred_badge(rating: str, score: float) -> str:
    css = {"High": "cred-badge--high", "Medium": "cred-badge--medium", "Low": "cred-badge--low"}.get(
        rating, "cred-badge--medium"
    )
    return f'<span class="cred-badge {css}">{rating} {score:.0%}</span>'


def render_source_card(
    title: str, url: str, rating: str, score: float, word_count: int, snippet: str = ""
) -> None:
    css = {"High": "source-card--high", "Medium": "source-card--medium", "Low": "source-card--low"}.get(
        rating, ""
    )
    badge = render_cred_badge(rating, score)
    domain = url.split("/")[2] if len(url.split("/")) > 2 else url
    snip = f'<p class="source-card__snippet">{snippet}</p>' if snippet else ""
    st.markdown(
        f'<div class="source-card {css}">'
        f'<div class="source-card__header">'
        f'<a href="{url}" target="_blank" class="source-card__title">{title}</a>'
        f"{badge}</div>"
        f'<div class="source-card__meta"><span>{domain}</span><span>{word_count:,} words</span></div>'
        f"{snip}</div>",
        unsafe_allow_html=True,
    )


def render_empty_state(icon: str, title: str, description: str) -> None:
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-state__icon">{icon}</div>'
        f'<div class="empty-state__title">{title}</div>'
        f'<div class="empty-state__desc">{description}</div></div>',
        unsafe_allow_html=True,
    )


def render_finding_row(number: int, text: str) -> None:
    st.markdown(
        f'<div class="finding-row"><span class="finding-row__number">{number:02d}</span>{text}</div>',
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, variant: str = "default") -> None:
    vcls = {"success": "metric-card--success", "warning": "metric-card--warning", "danger": "metric-card--danger"}.get(
        variant, ""
    )
    st.markdown(
        f'<div class="metric-card {vcls}"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar components
# ---------------------------------------------------------------------------


def render_sidebar_brand() -> None:
    st.markdown(
        '<div class="sidebar-brand">'
        '<span class="sidebar-brand__icon">🔬</span>'
        '<span class="sidebar-brand__text">Veridex</span>'
        '<span class="sidebar-brand__version">v1.0</span></div>',
        unsafe_allow_html=True,
    )


def render_sidebar_settings() -> None:
    st.divider()
    st.slider("Max sources", 2, 15, 6, key="max_sources")
    st.multiselect("Export formats", ["markdown", "pdf", "json"], default=["markdown"], key="export_formats")
    provider_options = ["DuckDuckGo"]
    if os.environ.get("TAVILY_API_KEY"):
        provider_options.append("Tavily")
    st.selectbox(
        "Search provider",
        provider_options,
        key="search_provider",
        help="Tavily requires TAVILY_API_KEY to be set.",
    )


def render_sidebar_demo() -> None:
    st.divider()
    demo_queries = get_demo_queries()
    st.selectbox("Demo query", ["(none)"] + demo_queries, key="demo_query")
    if st.button("Load Demo", type="primary", use_container_width=True):
        sel = st.session_state.get("demo_query", "(none)")
        if sel != "(none)":
            st.session_state["demo_data"] = get_demo_result(sel)
            st.session_state["demo_active"] = True
            st.session_state["active_query"] = sel
            st.session_state["_pending_nav"] = "Research"
            st.rerun()


def render_sidebar_footer() -> None:
    st.markdown(
        '<div class="sidebar-footer">Built with Streamlit + spaCy<br>Veridex v1.0</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Results rendering (shared between live & demo)
# ---------------------------------------------------------------------------


def _render_results_common(
    *,
    sources_count: int,
    key_sentences: list[str],
    statistics: list[str],
    claims: list[str],
    summary: str,
    entities: dict[str, list[str]],
    key_phrases: list[str],
    consensus_points: list[str],
    conflict_points: list[str],
    sources_data: list[dict[str, Any]],
    md_report: str | None = None,
    agent: ResearchAgent | None = None,
    query: str = "",
    export_formats: list[str] | None = None,
    result_obj: ResearchResult | None = None,
) -> None:
    avg_cred = sum(s["credibility_score"] for s in sources_data) / max(len(sources_data), 1)
    cols = st.columns(4)
    cols[0].metric("Sources Analyzed", sources_count)
    cols[1].metric("Key Findings", len(key_sentences))
    cols[2].metric("Statistics Found", len(statistics))
    cols[3].metric("Avg Credibility", f"{avg_cred:.0%}")

    st.markdown(f'<div class="summary-container">{summary}</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Findings", "Entities & Topics", "Sources", "Full Report"])

    with tabs[0]:
        if key_sentences:
            st.subheader("Key Findings")
            for i, s in enumerate(key_sentences, 1):
                render_finding_row(i, s)
        if statistics:
            st.subheader("Statistics & Data")
            for stat in statistics:
                st.markdown(f'<div class="stat-card">{stat}</div>', unsafe_allow_html=True)
        if claims:
            st.subheader("Notable Claims")
            for claim in claims:
                st.markdown(f'<div class="stat-card">{claim}</div>', unsafe_allow_html=True)

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Named Entities")
            if entities:
                for label, ents in entities.items():
                    pills = " ".join(f'<span class="entity-pill">{e}</span>' for e in ents[:8])
                    st.markdown(f"**{label}**", unsafe_allow_html=True)
                    st.markdown(pills, unsafe_allow_html=True)
            else:
                st.info("No entities extracted.")
        with c2:
            st.subheader("Key Topics")
            if key_phrases:
                pills = " ".join(f'<span class="entity-pill">{p}</span>' for p in key_phrases[:15])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.info("No key phrases extracted.")

    with tabs[2]:
        # Radar chart for source credibility
        if sources_data and len(sources_data) >= 2:
            st.subheader("Source Credibility Radar")
            _render_radar_chart(sources_data)

        if consensus_points:
            st.subheader("Source Consensus")
            for pt in consensus_points:
                st.markdown(f'<div class="consensus-card">{pt}</div>', unsafe_allow_html=True)
        if conflict_points:
            st.subheader("Conflicting Information")
            for pt in conflict_points:
                st.markdown(f'<div class="conflict-card">{pt}</div>', unsafe_allow_html=True)

        # Claim verification visual
        if claims and sources_data:
            st.subheader("Claim Verification")
            _render_claim_verification(claims[:5], sources_data)

        st.subheader("All Sources")
        for src in sorted(sources_data, key=lambda s: s["credibility_score"], reverse=True):
            render_source_card(
                title=src["title"],
                url=src["url"],
                rating=src["credibility_rating"],
                score=src["credibility_score"],
                word_count=src["word_count"],
                snippet=src.get("snippet", ""),
            )

    with tabs[3]:
        if md_report:
            st.markdown(md_report)
            st.divider()
            st.subheader("Export Report")
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                st.download_button(
                    "Download Markdown",
                    data=md_report,
                    file_name=f"research_{query[:30].replace(' ', '_')}.md",
                    mime="text/markdown",
                )
            if agent and result_obj and result_obj.report_data:
                fmts = export_formats or ["markdown"]
                with ec2:
                    if "pdf" in fmts:
                        paths = agent.export_report(result_obj, formats=["pdf"])
                        if "pdf" in paths:
                            with open(paths["pdf"], "rb") as f:
                                st.download_button(
                                    "Download PDF",
                                    data=f.read(),
                                    file_name=f"research_{query[:30].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                )
                with ec3:
                    if "json" in fmts:
                        paths = agent.export_report(result_obj, formats=["json"])
                        if "json" in paths:
                            with open(paths["json"]) as f:
                                st.download_button(
                                    "Download JSON",
                                    data=f.read(),
                                    file_name=f"research_{query[:30].replace(' ', '_')}.json",
                                    mime="application/json",
                                )
        else:
            st.info("Full report not available in demo mode.")


def _render_radar_chart(sources_data: list[dict[str, Any]]) -> None:
    """Render a radar/spider chart showing multi-dimensional source credibility."""
    categories = ["Credibility", "Content Depth", "Domain Trust"]
    fig = go.Figure()
    for i, src in enumerate(sources_data[:6]):
        cred = src["credibility_score"]
        depth = min(src["word_count"] / 10000, 1.0)
        domain_trust = cred * 0.9 + 0.1 if cred > 0.8 else cred * 0.7
        vals = [cred, depth, domain_trust]
        vals.append(vals[0])  # close the polygon
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories + [categories[0]],
            fill="toself",
            name=src["title"][:30],
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)]),
            opacity=0.7,
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#1e1e2e", color="#8e8ea0"),
            angularaxis=dict(gridcolor="#1e1e2e", color="#8e8ea0"),
        ),
        showlegend=True,
        title="Source Bias Radar",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_claim_verification(claims: list[str], sources_data: list[dict[str, Any]]) -> None:
    """Show which sources likely relate to each claim."""
    src_names = [s["title"][:25] for s in sources_data[:8]]
    for claim in claims:
        claim_words = {w.lower() for w in claim.split() if len(w) > 4}
        matches: list[str] = []
        for src in sources_data[:8]:
            title_words = {w.lower() for w in src["title"].split() if len(w) > 3}
            snippet_words = {w.lower() for w in src.get("snippet", "").split() if len(w) > 3}
            overlap = claim_words & (title_words | snippet_words)
            if overlap:
                matches.append(src["title"][:30])
        badge_html = " ".join(
            f'<span class="cred-badge cred-badge--high">{m}</span>' for m in matches
        ) if matches else '<span class="cred-badge cred-badge--low">No direct match</span>'
        st.markdown(
            f'<div class="stat-card"><strong>Claim:</strong> {claim[:120]}...<br>'
            f'<strong>Supported by:</strong> {badge_html}</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# PAGE: Dashboard
# ---------------------------------------------------------------------------


def page_dashboard(agent: ResearchAgent) -> None:
    st.markdown('<p class="hero-title">Veridex</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">Autonomous web research agent &mdash; search, scrape, analyze, '
        "and synthesize from multiple sources. No API keys required.</p>",
        unsafe_allow_html=True,
    )
    tags = ["DuckDuckGo Search", "NLP Extraction", "Credibility Scoring", "Multi-Source Synthesis", "Export Reports"]
    st.markdown(
        '<div style="margin-bottom:1.5rem;">'
        + "".join(f'<span class="feature-tag">{t}</span>' for t in tags)
        + "</div>",
        unsafe_allow_html=True,
    )

    # Query input
    query = st.text_input(
        "What would you like to research today?",
        value="",
        placeholder="e.g., Impact of AI on climate change research",
        key="dashboard_query",
    )
    if st.button("Start Research", type="primary"):
        if query:
            st.session_state["active_query"] = query
            st.session_state["_pending_nav"] = "Research"
            st.rerun()
        else:
            st.warning("Please enter a research query.")

    # Quick stats
    records = agent.storage.get_history(limit=999)
    total = len(records)
    total_sources = sum(r.num_sources for r in records)
    latest = records[0].created_at[:10] if records else "None yet"

    cols = st.columns(4)
    with cols[0]:
        render_metric_card("Total Researches", str(total))
    with cols[1]:
        render_metric_card("Sources Analyzed", str(total_sources))
    with cols[2]:
        render_metric_card("Avg Sources/Query", f"{total_sources / max(total, 1):.1f}")
    with cols[3]:
        render_metric_card("Latest Research", latest)

    # Recent research
    if records:
        st.subheader("Recent Research")
        recent = records[:5]
        rcols = st.columns(len(recent))
        for i, r in enumerate(recent):
            with rcols[i]:
                st.markdown(
                    f'<div class="demo-card">'
                    f'<div class="demo-card__title">{r.query[:50]}</div>'
                    f'<div class="demo-card__desc">{r.created_at[:10]} &bull; {r.num_sources} sources</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Re-run", key=f"dash_rerun_{r.id}"):
                    st.session_state["active_query"] = r.query
                    st.session_state["_pending_nav"] = "Research"
                    st.rerun()
    else:
        # Demo showcase
        render_empty_state("🔍", "No research yet", "Enter a query above to get started, or try a demo below.")
        st.subheader("Try a Demo")
        demo_queries = get_demo_queries()
        demo_descs = {
            "Impact of AI on healthcare": "Explore how AI is transforming diagnostics, drug discovery, and clinical care.",
            "Quantum computing breakthroughs 2024": "Discover the latest quantum computing milestones and future outlook.",
            "Climate change and renewable energy 2024": "Analyze the global renewable energy transition and climate progress.",
        }
        dcols = st.columns(min(3, len(demo_queries)))
        for i, dq in enumerate(demo_queries[:3]):
            with dcols[i]:
                st.markdown(
                    f'<div class="demo-card">'
                    f'<div class="demo-card__title">{dq}</div>'
                    f'<div class="demo-card__desc">{demo_descs.get(dq, "Pre-cached demo results.")}</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Try it", key=f"demo_try_{i}"):
                    st.session_state["demo_data"] = get_demo_result(dq)
                    st.session_state["demo_active"] = True
                    st.session_state["active_query"] = dq
                    st.session_state["_pending_nav"] = "Research"
                    st.rerun()


# ---------------------------------------------------------------------------
# PAGE: Research
# ---------------------------------------------------------------------------


def page_research(agent: ResearchAgent) -> None:
    qcol, bcol = st.columns([5, 1])
    with qcol:
        query = st.text_input(
            "Research query",
            value=st.session_state.get("active_query", ""),
            placeholder="Enter your research query",
            key="research_query_input",
            label_visibility="collapsed",
        )
    with bcol:
        run_clicked = st.button("Research", type="primary", use_container_width=True)

    # Demo mode banner
    if st.session_state.get("demo_active") and st.session_state.get("demo_data"):
        data = st.session_state["demo_data"]
        st.info(f"**Demo Mode** -- Showing cached results for: *{data['query']}*")
        if st.button("Clear demo"):
            st.session_state.pop("demo_active", None)
            st.session_state.pop("demo_data", None)
            st.rerun()
        _render_demo_results(data)
        return

    if run_clicked and query:
        st.session_state["active_query"] = query
        _run_live_research(agent, query)
    elif run_clicked and not query:
        st.warning("Please enter a research query.")
    elif st.session_state.get("research_result"):
        result = st.session_state["research_result"]
        _render_live_results(result, agent)
    else:
        render_empty_state("🔍", "Enter a research query", "Type a question above and click Research to begin.")


def _run_live_research(agent: ResearchAgent, query: str) -> None:
    max_sources = st.session_state.get("max_sources", 6)
    export_formats = st.session_state.get("export_formats", ["markdown"])
    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_cb(msg: str, pct: float) -> None:
        progress_bar.progress(min(pct, 1.0))
        status_text.text(msg)

    with st.spinner("Researching..."):
        result = agent.research(query, max_sources=max_sources, progress_cb=progress_cb)

    progress_bar.empty()
    status_text.empty()

    if not result.sources:
        st.error("No sources could be analyzed. Try a different or broader query.")
        if st.button("Retry"):
            st.rerun()
        return

    st.session_state["research_result"] = result
    _render_live_results(result, agent)


def _render_live_results(result: ResearchResult, agent: ResearchAgent) -> None:
    sources_data = [
        {
            "url": s.search_result.url,
            "title": s.page.title if s.page else s.search_result.title,
            "credibility_score": s.credibility_score,
            "credibility_rating": s.credibility_rating,
            "word_count": s.page.word_count if s.page else 0,
            "snippet": s.search_result.snippet,
        }
        for s in result.sources
    ]
    md_report = None
    if result.report_data:
        gen = ReportGenerator()
        md_report = gen.generate_markdown(result.report_data)

    _render_results_common(
        sources_count=len(result.sources),
        key_sentences=result.key_sentences,
        statistics=result.statistics,
        claims=result.claims,
        summary=result.summary,
        entities=result.merged_entities,
        key_phrases=result.key_phrases,
        consensus_points=result.consensus_points,
        conflict_points=result.conflict_points,
        sources_data=sources_data,
        md_report=md_report,
        agent=agent,
        query=result.query,
        export_formats=st.session_state.get("export_formats", ["markdown"]),
        result_obj=result,
    )


def _render_demo_results(data: dict[str, Any]) -> None:
    sources_data = data.get("sources", [])
    _render_results_common(
        sources_count=len(sources_data),
        key_sentences=data.get("key_sentences", []),
        statistics=data.get("statistics", []),
        claims=data.get("claims", []),
        summary=data.get("summary", ""),
        entities=data.get("entities", {}),
        key_phrases=data.get("key_phrases", []),
        consensus_points=data.get("consensus_points", []),
        conflict_points=data.get("conflict_points", []),
        sources_data=sources_data,
    )


# ---------------------------------------------------------------------------
# PAGE: History
# ---------------------------------------------------------------------------


def page_history(agent: ResearchAgent) -> None:
    st.markdown('<p class="hero-title">Research History</p>', unsafe_allow_html=True)
    st.caption("Browse and manage your past research sessions")

    fc1, fc2, fc3 = st.columns([4, 2, 2])
    with fc1:
        search_q = st.text_input("Search history", placeholder="Filter by query...", key="history_search")
    with fc2:
        sort_by = st.selectbox("Sort by", ["Newest first", "Oldest first", "Most sources", "Fewest sources"], key="history_sort")
    with fc3:
        time_range = st.selectbox("Time range", ["All time", "Today", "This week", "This month"], key="history_range")

    if search_q:
        records = agent.storage.search_history(search_q)
    else:
        records = agent.storage.get_history(limit=999)

    # Time filter
    now = datetime.utcnow()
    if time_range == "Today":
        records = [r for r in records if r.created_at[:10] == now.strftime("%Y-%m-%d")]
    elif time_range == "This week":
        week_ago = (now - timedelta(days=7)).isoformat()
        records = [r for r in records if r.created_at >= week_ago]
    elif time_range == "This month":
        month_ago = (now - timedelta(days=30)).isoformat()
        records = [r for r in records if r.created_at >= month_ago]

    # Sort
    if sort_by == "Oldest first":
        records = sorted(records, key=lambda r: r.created_at)
    elif sort_by == "Most sources":
        records = sorted(records, key=lambda r: r.num_sources, reverse=True)
    elif sort_by == "Fewest sources":
        records = sorted(records, key=lambda r: r.num_sources)

    # Stats row
    total = len(records)
    total_src = sum(r.num_sources for r in records)
    if records:
        earliest = min(r.created_at[:10] for r in records)
        latest = max(r.created_at[:10] for r in records)
        span = f"{earliest} to {latest}"
    else:
        span = "N/A"

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Total Sessions", total)
    sc2.metric("Total Sources", total_src)
    sc3.metric("Time Span", span)

    if not records:
        render_empty_state("📚", "No research history", "Run your first query from the Dashboard.")
        if st.button("Go to Dashboard"):
            st.session_state["_pending_nav"] = "Dashboard"
            st.rerun()
        return

    # Pagination
    page_size = 20
    page_num = st.session_state.get("history_page", 0)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page_num = min(page_num, total_pages - 1)
    page_records = records[page_num * page_size : (page_num + 1) * page_size]

    for r in page_records:
        title = f"{r.query[:50]} - {r.created_at[:10]} - {r.num_sources} sources"
        with st.expander(title):
            if r.summary:
                st.write(r.summary[:300])
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                if st.button("Re-run", key=f"hist_rerun_{r.id}"):
                    st.session_state["active_query"] = r.query
                    st.session_state["_pending_nav"] = "Research"
                    st.rerun()
            with ac2:
                if st.button("View Details", key=f"hist_view_{r.id}"):
                    st.write(f"**Query:** {r.query}")
                    st.write(f"**Date:** {r.created_at}")
                    st.write(f"**Sources:** {r.num_sources}")
                    if r.summary:
                        st.write(r.summary)
            with ac3:
                confirm_key = f"confirm_delete_{r.id}"
                if st.session_state.get(confirm_key):
                    st.warning("Are you sure?")
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("Confirm Delete", key=f"del_yes_{r.id}"):
                            agent.storage.delete_session(r.id)
                            st.session_state.pop(confirm_key, None)
                            st.rerun()
                    with dc2:
                        if st.button("Cancel", key=f"del_no_{r.id}"):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()
                else:
                    if st.button("Delete", key=f"hist_del_{r.id}"):
                        st.session_state[confirm_key] = True
                        st.rerun()

    # Pagination controls
    if total_pages > 1:
        pc1, pc2, pc3 = st.columns([1, 2, 1])
        with pc1:
            if st.button("Previous", disabled=page_num == 0):
                st.session_state["history_page"] = page_num - 1
                st.rerun()
        with pc2:
            st.markdown(f"<div style='text-align:center;color:var(--text-secondary);'>Page {page_num + 1} of {total_pages}</div>", unsafe_allow_html=True)
        with pc3:
            if st.button("Next", disabled=page_num >= total_pages - 1):
                st.session_state["history_page"] = page_num + 1
                st.rerun()


# ---------------------------------------------------------------------------
# PAGE: Analytics
# ---------------------------------------------------------------------------


def page_analytics(agent: ResearchAgent) -> None:
    st.markdown('<p class="hero-title">Analytics</p>', unsafe_allow_html=True)
    st.caption("Insights from your research history")

    records = agent.storage.get_history(limit=999)

    if not records:
        render_empty_state("📈", "No research data yet", "Complete some research queries to see analytics here.")
        if st.button("Go to Dashboard"):
            st.session_state["_pending_nav"] = "Dashboard"
            st.rerun()
        return

    total = len(records)
    total_sources = sum(r.num_sources for r in records)
    avg_sources = total_sources / max(total, 1)

    # Get source-level data for credibility
    all_sources = agent.storage.get_all_sources()
    avg_cred = (
        sum(s["credibility_score"] for s in all_sources) / len(all_sources)
        if all_sources
        else 0
    )

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Sessions", total)
    mc2.metric("Total Sources", total_sources)
    mc3.metric("Avg Sources/Query", f"{avg_sources:.1f}")
    mc4.metric("Avg Credibility", f"{avg_cred:.0%}" if all_sources else "N/A")

    if total < 3:
        st.info("Run more queries to unlock all analytics.")

    # Chart Row 1
    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("Research Activity Over Time")
        if total >= 2:
            dates: dict[str, int] = {}
            for r in records:
                d = r.created_at[:10]
                dates[d] = dates.get(d, 0) + 1
            sorted_dates = sorted(dates.items())
            fig = go.Figure(
                data=go.Scatter(
                    x=[d[0] for d in sorted_dates],
                    y=[d[1] for d in sorted_dates],
                    mode="lines+markers",
                    line=dict(color="#6c63ff", width=2),
                    marker=dict(size=8, color="#6c63ff"),
                )
            )
            fig.update_layout(**PLOTLY_LAYOUT, title="Sessions per Day")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Not enough data yet.")

    with ch2:
        st.subheader("Sources Per Query")
        last10 = records[:10]
        fig = go.Figure(
            data=go.Bar(
                x=[r.query[:25] for r in last10],
                y=[r.num_sources for r in last10],
                marker=dict(
                    color=[CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(last10))],
                ),
            )
        )
        fig.update_layout(**PLOTLY_LAYOUT, title="Last 10 Queries")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Chart Row 2
    ch3, ch4 = st.columns(2)

    with ch3:
        st.subheader("Credibility Distribution")
        if all_sources:
            high = sum(1 for s in all_sources if s["credibility_score"] >= 0.8)
            medium = sum(1 for s in all_sources if 0.5 <= s["credibility_score"] < 0.8)
            low = sum(1 for s in all_sources if s["credibility_score"] < 0.5)
            fig = go.Figure(
                data=go.Pie(
                    labels=["High", "Medium", "Low"],
                    values=[high, medium, low],
                    hole=0.4,
                    marker=dict(colors=["#22c55e", "#eab308", "#ef4444"]),
                )
            )
            fig.update_layout(**PLOTLY_LAYOUT, title="Source Credibility")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No source data available.")

    with ch4:
        st.subheader("Top Researched Topics")
        all_words: list[str] = []
        for r in records:
            words = [w.lower() for w in r.query.split() if w.lower() not in STOPWORDS and len(w) > 2]
            all_words.extend(words)
        if all_words:
            counter = Counter(all_words).most_common(10)
            fig = go.Figure(
                data=go.Bar(
                    y=[w[0] for w in reversed(counter)],
                    x=[w[1] for w in reversed(counter)],
                    orientation="h",
                    marker=dict(color="#a855f7"),
                )
            )
            fig.update_layout(**PLOTLY_LAYOUT, title="Top 10 Keywords")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Not enough data.")

    # Chart Row 3 - Timeline scatter
    if total >= 3:
        st.subheader("Research Timeline")
        fig = go.Figure(
            data=go.Scatter(
                x=[r.created_at[:10] for r in records],
                y=[r.num_sources for r in records],
                mode="markers",
                marker=dict(
                    size=[max(8, min(40, len(r.summary) // 10)) for r in records],
                    color=[i / total for i in range(total)],
                    colorscale="Purples",
                    showscale=True,
                    colorbar=dict(title="Index"),
                ),
                text=[r.query[:50] for r in records],
                hovertemplate="<b>%{text}</b><br>Sources: %{y}<extra></extra>",
            )
        )
        fig.update_layout(**PLOTLY_LAYOUT, title="Research Depth Over Time")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# PAGE: About
# ---------------------------------------------------------------------------


def page_about(agent: ResearchAgent) -> None:
    st.markdown('<p class="hero-title">About Veridex</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">An autonomous web research agent built for hackathon P4. '
        "Zero API keys. Full pipeline transparency. Local NLP.</p>",
        unsafe_allow_html=True,
    )

    st.subheader("How It Works")
    steps = [
        ("1", "🔍", "Search", "Queries DuckDuckGo for relevant sources"),
        ("2", "🌐", "Scrape", "Extracts content from web pages (robots.txt aware)"),
        ("3", "🧠", "Analyze", "NLP fact extraction with spaCy"),
        ("4", "🛡️", "Score", "Rates source credibility (domain, HTTPS, trust)"),
        ("5", "✨", "Synthesize", "TF-IDF summarization across documents"),
        ("6", "📄", "Report", "Generates structured reports with citations"),
    ]
    row1 = st.columns(3)
    row2 = st.columns(3)
    for i, (num, icon, title, desc) in enumerate(steps):
        col = row1[i] if i < 3 else row2[i - 3]
        with col:
            st.markdown(
                f'<div class="step-card">'
                f'<div class="step-card__number">{num}</div>'
                f'<div class="step-card__icon">{icon}</div>'
                f'<div class="step-card__title">{title}</div>'
                f'<div class="step-card__desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    st.subheader("Architecture")
    st.graphviz_chart(
        """
digraph G {
    bgcolor="transparent"
    node [shape=box, style="rounded,filled", fillcolor="#12121a",
          fontcolor="#ececf1", color="#6c63ff", fontname="Inter", fontsize=11]
    edge [color="#6c63ff", arrowsize=0.7, penwidth=1.5]

    Query -> SearchEngine
    SearchEngine -> WebScraper
    WebScraper -> FactExtractor
    FactExtractor -> CredibilityScorer
    CredibilityScorer -> Summarizer
    Summarizer -> ReportGenerator
    ReportGenerator -> Storage

    Query [label="Query Input", fillcolor="#1a1a28"]
    SearchEngine [label="DuckDuckGo\\nSearch"]
    WebScraper [label="Web Scraper\\n(robots.txt)"]
    FactExtractor [label="spaCy NLP\\nExtractor"]
    CredibilityScorer [label="Credibility\\nScorer"]
    Summarizer [label="TF-IDF\\nSummarizer"]
    ReportGenerator [label="Report\\nGenerator"]
    Storage [label="SQLite\\nStorage", fillcolor="#1a1a28"]
}
"""
    )

    # Tech stack
    st.subheader("Tech Stack")
    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown("**Core Technologies**")
        techs = [
            "Python 3.12+",
            "Streamlit (UI framework)",
            "spaCy (NLP)",
            "DuckDuckGo Search",
            "SQLite (storage)",
            "Plotly (charts)",
        ]
        for t in techs:
            st.markdown(f"- {t}")
    with tc2:
        st.markdown("**Key Features**")
        features = [
            "No API keys required",
            "robots.txt compliance",
            "Multi-format export (MD/PDF/JSON)",
            "Credibility scoring engine",
            "Demo mode for offline presentations",
            "Research history tracking",
        ]
        for f in features:
            st.markdown(f"- {f}")

    st.divider()
    st.caption("Built for P4 Hackathon | Veridex v1.0")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    inject_css()
    # SVG favicon for sharper rendering in browser tabs
    st.markdown(
        '<link rel="icon" type="image/svg+xml" '
        "href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
        "<text y='.9em' font-size='90'>&#x1F52C;</text></svg>\">",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        render_sidebar_brand()

        # Handle pending navigation requests (set before widget instantiation)
        _pending_nav = st.session_state.pop("_pending_nav", None)
        _nav_options = ["Dashboard", "Research", "History", "Analytics", "About"]
        if _pending_nav in _nav_options:
            st.session_state["nav_page"] = _pending_nav

        page = st.radio(
            "nav",
            _nav_options,
            format_func=lambda x: {
                "Dashboard": "📊  Dashboard",
                "Research": "🔬  Research",
                "History": "📚  History",
                "Analytics": "📈  Analytics",
                "About": "ℹ️  About",
            }[x],
            label_visibility="collapsed",
            key="nav_page",
        )

        if page in ("Dashboard", "Research"):
            render_sidebar_settings()

        if page == "Dashboard":
            render_sidebar_demo()

        render_sidebar_footer()

    selected_provider = st.session_state.get("search_provider", "DuckDuckGo").lower()
    agent = get_agent(selected_provider)

    pages = {
        "Dashboard": page_dashboard,
        "Research": page_research,
        "History": page_history,
        "Analytics": page_analytics,
        "About": page_about,
    }
    pages[page](agent)


if __name__ == "__main__":
    main()
