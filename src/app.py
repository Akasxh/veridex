"""Streamlit web interface for ResearchBot."""

from __future__ import annotations

import streamlit as st

try:
    from src.agent import ResearchAgent
    from src.demo import get_demo_queries, get_demo_result
    from src.report import ReportGenerator
except ImportError:
    from agent import ResearchAgent  # type: ignore[no-redef]
    from demo import get_demo_queries, get_demo_result  # type: ignore[no-redef]
    from report import ReportGenerator  # type: ignore[no-redef]

st.set_page_config(
    page_title="ResearchBot -- AI Web Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "ResearchBot -- Autonomous web research with DuckDuckGo search, NLP summarization, and credibility scoring. No API keys required.",
    },
)

# Custom CSS for a polished look
st.markdown("""
<style>
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    .stApp { max-width: 1200px; margin: 0 auto; }

    /* Sidebar gradient */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        color: #a0c4ff !important;
        font-weight: 600;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    div[data-testid="stMetric"] label { color: rgba(255,255,255,0.85) !important; font-size: 0.85rem; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; font-weight: 700; }

    /* Hero styling */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle { font-size: 1.15rem; color: #666; margin-top: 4px; line-height: 1.5; }

    /* Feature tags */
    .tag {
        display: inline-block;
        background: linear-gradient(135deg, #e8f0fe, #f0e6ff);
        color: #4a3aad;
        padding: 4px 14px;
        border-radius: 16px;
        font-size: 0.85rem;
        margin: 3px 4px;
        font-weight: 500;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    /* Credibility badges */
    .cred-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .cred-high { background: #d4edda; color: #155724; border: 1px solid #28a745; }
    .cred-medium { background: #fff3cd; color: #856404; border: 1px solid #ffc107; }
    .cred-low { background: #f8d7da; color: #721c24; border: 1px solid #dc3545; }

    /* Source cards */
    .source-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .source-card-high { border-left-color: #28a745; }
    .source-card-medium { border-left-color: #ffc107; }
    .source-card-low { border-left-color: #dc3545; }
    .source-card h4 { margin: 0 0 6px 0; font-size: 1rem; }
    .source-card .meta { color: #666; font-size: 0.85rem; }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 6px 0;
        border-left: 3px solid #667eea;
        font-size: 0.95rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def _cred_badge(rating: str, score: float) -> str:
    """Generate HTML for a credibility badge."""
    css_class = {"High": "cred-high", "Medium": "cred-medium", "Low": "cred-low"}.get(rating, "cred-medium")
    return f'<span class="cred-badge {css_class}">{rating} {score:.0%}</span>'


def _source_card_html(title: str, url: str, rating: str, score: float, word_count: int, snippet: str = "") -> str:
    """Generate HTML for a source card with credibility indicator."""
    css_class = {"High": "source-card-high", "Medium": "source-card-medium", "Low": "source-card-low"}.get(rating, "")
    badge = _cred_badge(rating, score)
    snippet_html = f'<p style="margin:4px 0 0;color:#555;font-size:0.9rem;">{snippet}</p>' if snippet else ""
    return (
        f'<div class="source-card {css_class}">'
        f'<h4><a href="{url}" target="_blank" style="color:#1a1a2e;text-decoration:none;">{title}</a></h4>'
        f'<span class="meta">{badge} &nbsp; {word_count:,} words</span>'
        f'{snippet_html}'
        f'</div>'
    )


@st.cache_resource
def get_agent() -> ResearchAgent:
    return ResearchAgent()


def main() -> None:
    # Hero section
    st.markdown('<p class="hero-title">🔬 ResearchBot</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">Autonomous web research agent &mdash; search, scrape, summarize, and synthesize from multiple sources. No API keys required.</p>',
        unsafe_allow_html=True,
    )

    # Feature tags
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<span class="tag">DuckDuckGo Search</span>'
        '<span class="tag">TF-IDF Summarization</span>'
        '<span class="tag">spaCy NLP</span>'
        '<span class="tag">Credibility Scoring</span>'
        '<span class="tag">Multi-Source Synthesis</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    agent = get_agent()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        max_sources = st.slider("Max sources to analyze", 2, 15, 6)
        export_formats = st.multiselect(
            "Export formats", ["markdown", "pdf", "json"], default=["markdown"]
        )

        st.divider()

        # Demo mode
        st.header("🎯 Demo Mode")
        st.caption("Pre-cached results for instant demos -- no network needed.")
        demo_queries = get_demo_queries()
        demo_query = st.selectbox("Select demo query", ["(none)"] + demo_queries)
        if demo_query != "(none)":
            if st.button("Load Demo", type="primary", use_container_width=True):
                st.session_state["demo_data"] = get_demo_result(demo_query)
                st.session_state["demo_active"] = True
                st.rerun()

        st.divider()

        # History
        st.header("📚 Research History")
        records = agent.storage.get_history(limit=10)
        if records:
            for r in records:
                with st.expander(f"{r.query[:40]}{'...' if len(r.query) > 40 else ''} ({r.created_at[:10]})"):
                    st.write(f"**Sources:** {r.num_sources}")
                    st.write(f"**Date:** {r.created_at[:19]}")
                    if r.summary:
                        st.write(r.summary[:200] + "...")
                    if st.button("Re-run", key=f"rerun_{r.id}"):
                        st.session_state["query_input"] = r.query
                        st.session_state.pop("demo_active", None)
                        st.rerun()
        else:
            st.info("No research history yet. Run a query to get started!")

    # Check for demo mode
    if st.session_state.get("demo_active") and st.session_state.get("demo_data"):
        _render_demo(st.session_state["demo_data"])
        if st.button("← Clear demo results"):
            st.session_state.pop("demo_active", None)
            st.session_state.pop("demo_data", None)
            st.rerun()
        return

    # Main query area
    query = st.text_input(
        "🔍 Enter your research query",
        value=st.session_state.get("query_input", ""),
        placeholder="e.g., Impact of AI on climate change research",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        run_clicked = st.button("🚀 Research", type="primary", use_container_width=True)

    if run_clicked and query:
        _run_research(agent, query, max_sources, export_formats)
    elif run_clicked and not query:
        st.warning("Please enter a research query.")


def _render_demo(data: dict) -> None:
    """Render pre-cached demo results."""
    st.info(f"**Demo Mode** -- Showing pre-cached results for: *{data['query']}*")

    # Metrics row
    cols = st.columns(4)
    cols[0].metric("Sources Analyzed", len(data["sources"]))
    cols[1].metric("Key Findings", len(data.get("key_sentences", [])))
    cols[2].metric("Statistics Found", len(data.get("statistics", [])))
    avg_cred = sum(s["credibility_score"] for s in data["sources"]) / max(len(data["sources"]), 1)
    cols[3].metric("Avg Credibility", f"{avg_cred:.0%}")

    # Summary
    st.header("Summary")
    st.write(data["summary"])

    # Tabs
    tabs = st.tabs(["Key Findings", "Facts & Entities", "Source Analysis"])

    with tabs[0]:
        if data.get("key_sentences"):
            st.subheader("Key Findings")
            for i, s in enumerate(data["key_sentences"], 1):
                st.markdown(f"**{i}.** {s}")

        if data.get("statistics"):
            st.subheader("Statistics & Data Points")
            for stat in data["statistics"]:
                st.markdown(f'<div class="stat-card">{stat}</div>', unsafe_allow_html=True)

        if data.get("claims"):
            st.subheader("Notable Claims")
            for claim in data["claims"]:
                st.info(claim)

    with tabs[1]:
        col_ent, col_phrases = st.columns(2)
        with col_ent:
            st.subheader("Named Entities")
            if data.get("entities"):
                for label, entities in data["entities"].items():
                    st.markdown(f"**{label}:** {', '.join(entities[:8])}")
            else:
                st.info("No entities extracted.")
        with col_phrases:
            st.subheader("Key Topics")
            if data.get("key_phrases"):
                for phrase in data["key_phrases"][:15]:
                    st.markdown(f"- {phrase}")

    with tabs[2]:
        if data.get("consensus_points"):
            st.subheader("Source Consensus")
            for point in data["consensus_points"]:
                st.success(point)
        if data.get("conflict_points"):
            st.subheader("Conflicting Information")
            for point in data["conflict_points"]:
                st.warning(point)

        st.subheader("Sources")
        for src in data["sources"]:
            st.markdown(
                _source_card_html(
                    title=src["title"],
                    url=src["url"],
                    rating=src["credibility_rating"],
                    score=src["credibility_score"],
                    word_count=src["word_count"],
                    snippet=src.get("snippet", ""),
                ),
                unsafe_allow_html=True,
            )


def _run_research(
    agent: ResearchAgent, query: str, max_sources: int, export_formats: list[str]
) -> None:
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
        st.error("No sources could be analyzed. Try a different query.")
        return

    # Metrics row
    cols = st.columns(4)
    cols[0].metric("Sources Analyzed", len(result.sources))
    cols[1].metric("Key Findings", len(result.key_sentences))
    cols[2].metric("Statistics Found", len(result.statistics))
    avg_cred = sum(s.credibility_score for s in result.sources) / max(len(result.sources), 1)
    cols[3].metric("Avg Credibility", f"{avg_cred:.0%}")

    # Summary
    st.header("Summary")
    st.write(result.summary)

    # Tabs for different sections
    tabs = st.tabs(["Key Findings", "Facts & Entities", "Source Analysis", "Full Report"])

    with tabs[0]:
        if result.key_sentences:
            st.subheader("Key Findings")
            for i, s in enumerate(result.key_sentences, 1):
                st.markdown(f"**{i}.** {s}")

        if result.statistics:
            st.subheader("Statistics & Data Points")
            for stat in result.statistics:
                st.markdown(f'<div class="stat-card">{stat}</div>', unsafe_allow_html=True)

        if result.claims:
            st.subheader("Notable Claims")
            for claim in result.claims:
                st.info(claim)

    with tabs[1]:
        col_ent, col_phrases = st.columns(2)

        with col_ent:
            st.subheader("Named Entities")
            if result.merged_entities:
                for label, entities in result.merged_entities.items():
                    st.markdown(f"**{label}:** {', '.join(entities[:8])}")
            else:
                st.info("No entities extracted.")

        with col_phrases:
            st.subheader("Key Topics")
            if result.key_phrases:
                for phrase in result.key_phrases[:15]:
                    st.markdown(f"- {phrase}")
            else:
                st.info("No key phrases extracted.")

    with tabs[2]:
        if result.consensus_points:
            st.subheader("Source Consensus")
            for point in result.consensus_points:
                st.success(point)

        if result.conflict_points:
            st.subheader("Conflicting Information")
            for point in result.conflict_points:
                st.warning(point)

        st.subheader("Sources")
        for src in result.sources:
            title = src.page.title if src.page else src.search_result.title
            st.markdown(
                _source_card_html(
                    title=title,
                    url=src.search_result.url,
                    rating=src.credibility_rating,
                    score=src.credibility_score,
                    word_count=src.page.word_count if src.page else 0,
                    snippet=src.search_result.snippet,
                ),
                unsafe_allow_html=True,
            )

    with tabs[3]:
        if result.report_data:
            gen = ReportGenerator()
            md_content = gen.generate_markdown(result.report_data)
            st.markdown(md_content)

            st.divider()
            st.subheader("Export Report")

            exp_cols = st.columns(3)
            with exp_cols[0]:
                st.download_button(
                    "📄 Download Markdown",
                    data=md_content,
                    file_name=f"research_{query[:30].replace(' ', '_')}.md",
                    mime="text/markdown",
                )
            with exp_cols[1]:
                if "pdf" in export_formats:
                    paths = agent.export_report(result, formats=["pdf"])
                    if "pdf" in paths:
                        with open(paths["pdf"], "rb") as f:
                            st.download_button(
                                "📑 Download PDF",
                                data=f.read(),
                                file_name=f"research_{query[:30].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                            )
            with exp_cols[2]:
                if "json" in export_formats:
                    paths = agent.export_report(result, formats=["json"])
                    if "json" in paths:
                        with open(paths["json"]) as f:
                            st.download_button(
                                "📊 Download JSON",
                                data=f.read(),
                                file_name=f"research_{query[:30].replace(' ', '_')}.json",
                                mime="application/json",
                            )

            if export_formats:
                paths = agent.export_report(result, formats=export_formats)
                if paths:
                    st.info("Files saved: " + ", ".join(f"{k}: {v}" for k, v in paths.items()))


if __name__ == "__main__":
    main()
