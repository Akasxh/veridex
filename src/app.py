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
    .stApp { max-width: 1200px; margin: 0 auto; }
    div[data-testid="stMetric"] {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 12px 16px;
    }
    .hero-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 0; }
    .hero-subtitle { font-size: 1.1rem; color: #666; margin-top: 4px; }
    .tag { display: inline-block; background: #e8f0fe; color: #1a73e8; padding: 2px 10px;
           border-radius: 12px; font-size: 0.85rem; margin: 2px 4px; }
</style>
""", unsafe_allow_html=True)


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
                with st.expander(f"{r.query[:40]}... ({r.created_at[:10]})"):
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
    st.info(f"🎯 **Demo Mode** -- Showing pre-cached results for: *{data['query']}*")

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
                st.markdown(f"- {stat}")

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
        for i, src in enumerate(data["sources"], 1):
            with st.expander(f"{i}. [{src['credibility_rating']}] {src['title'][:60]}"):
                st.markdown(f"**URL:** [{src['url']}]({src['url']})")
                st.markdown(f"**Credibility:** {src['credibility_score']:.0%} ({src['credibility_rating']})")
                st.markdown(f"**Word Count:** {src['word_count']}")
                if src.get("snippet"):
                    st.markdown(f"**Snippet:** {src['snippet']}")


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
                st.markdown(f"- {stat}")

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
        for i, src in enumerate(result.sources, 1):
            title = src.page.title if src.page else src.search_result.title
            with st.expander(f"{i}. [{src.credibility_rating}] {title[:60]}"):
                st.markdown(f"**URL:** [{src.search_result.url}]({src.search_result.url})")
                st.markdown(f"**Credibility:** {src.credibility_score:.0%} ({src.credibility_rating})")
                st.markdown(f"**Word Count:** {src.page.word_count if src.page else 'N/A'}")
                if src.search_result.snippet:
                    st.markdown(f"**Snippet:** {src.search_result.snippet}")

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
