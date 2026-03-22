"""Streamlit web interface for ResearchBot."""

from __future__ import annotations

import streamlit as st

from src.agent import ResearchAgent

st.set_page_config(
    page_title="ResearchBot -- AI Web Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_agent() -> ResearchAgent:
    return ResearchAgent()


def main() -> None:
    st.title("ResearchBot")
    st.caption("AI Web Research Agent -- Search, Scrape, Summarize, Synthesize")

    agent = get_agent()

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        max_sources = st.slider("Max sources to analyze", 2, 15, 6)
        export_formats = st.multiselect(
            "Export formats", ["markdown", "pdf", "json"], default=["markdown"]
        )

        st.divider()

        # History
        st.header("Research History")
        records = agent.storage.get_history(limit=10)
        if records:
            for r in records:
                with st.expander(f"{r.query[:40]}... ({r.created_at[:10]})"):
                    st.write(f"**Sources:** {r.num_sources}")
                    st.write(f"**Date:** {r.created_at[:19]}")
                    if r.summary:
                        st.write(r.summary[:200] + "...")
                    if st.button(f"Re-run", key=f"rerun_{r.id}"):
                        st.session_state["query_input"] = r.query
                        st.rerun()
        else:
            st.info("No research history yet.")

    # Main area
    query = st.text_input(
        "Enter your research query",
        value=st.session_state.get("query_input", ""),
        placeholder="e.g., Impact of AI on climate change research",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        run_clicked = st.button("Research", type="primary", use_container_width=True)

    if run_clicked and query:
        _run_research(agent, query, max_sources, export_formats)
    elif run_clicked and not query:
        st.warning("Please enter a research query.")


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

    # Results
    st.success(f"Analyzed {len(result.sources)} sources")

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
        # Consensus / Conflicts
        if result.consensus_points:
            st.subheader("Source Consensus")
            for point in result.consensus_points:
                st.success(point)

        if result.conflict_points:
            st.subheader("Conflicting Information")
            for point in result.conflict_points:
                st.warning(point)

        # Sources table
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
            from src.report import ReportGenerator
            gen = ReportGenerator()
            md_content = gen.generate_markdown(result.report_data)
            st.markdown(md_content)

            # Export buttons
            st.divider()
            st.subheader("Export Report")

            exp_cols = st.columns(3)
            with exp_cols[0]:
                st.download_button(
                    "Download Markdown",
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
                                "Download PDF",
                                data=f.read(),
                                file_name=f"research_{query[:30].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                            )
            with exp_cols[2]:
                if "json" in export_formats:
                    import json
                    paths = agent.export_report(result, formats=["json"])
                    if "json" in paths:
                        with open(paths["json"]) as f:
                            st.download_button(
                                "Download JSON",
                                data=f.read(),
                                file_name=f"research_{query[:30].replace(' ', '_')}.json",
                                mime="application/json",
                            )

            # Save to disk
            if export_formats:
                paths = agent.export_report(result, formats=export_formats)
                if paths:
                    st.info("Files saved: " + ", ".join(f"{k}: {v}" for k, v in paths.items()))


if __name__ == "__main__":
    main()
