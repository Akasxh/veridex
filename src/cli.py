"""CLI interface for Veridex."""

from __future__ import annotations

import argparse
import logging
import sys

logger = logging.getLogger(__name__)

try:
    from src.agent import ResearchAgent
    from src.demo import get_demo_queries, get_demo_result
except ImportError:
    from agent import ResearchAgent  # type: ignore[no-redef]
    from demo import get_demo_queries, get_demo_result  # type: ignore[no-redef]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="veridex",
        description="Veridex -- AI Web Research Agent. Search, scrape, summarize, and synthesize.",
    )
    parser.add_argument("query", nargs="?", help="Research query/topic")
    parser.add_argument("-n", "--num-sources", type=int, default=6, help="Max sources to analyze (default: 6)")
    parser.add_argument(
        "-f", "--format", nargs="+", default=["markdown"],
        choices=["markdown", "pdf", "json"],
        help="Export formats (default: markdown)",
    )
    parser.add_argument("--history", action="store_true", help="Show research history")
    parser.add_argument("--search-history", type=str, help="Search past research sessions")
    parser.add_argument("--demo", action="store_true", help="Run with pre-cached demo results (no network)")
    parser.add_argument("--list-demos", action="store_true", help="List available demo queries")

    args = parser.parse_args()

    if args.list_demos:
        print("\n=== Available Demo Queries ===\n")
        for q in get_demo_queries():
            print(f"  - {q}")
        print(f"\nUsage: veridex --demo \"{get_demo_queries()[0]}\"")
        return

    agent = ResearchAgent()

    if args.demo:
        if not args.query:
            # Pick first demo query
            args.query = get_demo_queries()[0]
        _run_demo(args.query)
        return

    if args.history:
        _show_history(agent)
        return

    if args.search_history:
        _search_history(agent, args.search_history)
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    _run_research(agent, args.query, args.num_sources, args.format)


def _show_history(agent: ResearchAgent) -> None:
    records = agent.storage.get_history(limit=20)
    if not records:
        print("No research history found.")
        return

    print("\n=== Research History ===\n")
    for r in records:
        print(f"  [{r.id}] {r.query}")
        print(f"      Date: {r.created_at[:19]}  |  Sources: {r.num_sources}")
        if r.summary:
            print(f"      Summary: {r.summary[:100]}...")
        print()


def _search_history(agent: ResearchAgent, query: str) -> None:
    records = agent.storage.search_history(query)
    if not records:
        print(f"No results found for '{query}'.")
        return

    print(f"\n=== Search results for '{query}' ===\n")
    for r in records:
        print(f"  [{r.id}] {r.query}  ({r.created_at[:10]}, {r.num_sources} sources)")


def _run_research(agent: ResearchAgent, query: str, max_sources: int, formats: list[str]) -> None:
    print(f"\n{'='*60}")
    print(f"  Veridex -- Researching: {query}")
    print(f"{'='*60}\n")

    def progress(msg: str, pct: float) -> None:
        bar_len = 30
        filled = int(bar_len * pct)
        bar = "#" * filled + "-" * (bar_len - filled)
        print(f"\r  [{bar}] {pct:5.0%}  {msg:<50}", end="", flush=True)

    result = agent.research(query, max_sources=max_sources, progress_cb=progress)
    print("\n")

    if not result.sources:
        print("  No sources could be analyzed. Try a different query.")
        return

    # Print summary
    print(f"  Sources analyzed: {len(result.sources)}\n")
    print("  === SUMMARY ===\n")
    print(f"  {result.summary[:1000]}\n")

    # Key findings
    if result.key_sentences:
        print("  === KEY FINDINGS ===\n")
        for i, s in enumerate(result.key_sentences[:5], 1):
            print(f"  {i}. {s}")
        print()

    # Key topics
    if result.key_phrases:
        print(f"  === KEY TOPICS ===\n")
        print(f"  {', '.join(result.key_phrases[:10])}\n")

    # Statistics
    if result.statistics:
        print("  === STATISTICS ===\n")
        for stat in result.statistics[:5]:
            print(f"  - {stat}")
        print()

    # Consensus
    if result.consensus_points:
        print("  === SOURCE CONSENSUS ===\n")
        for p in result.consensus_points:
            print(f"  + {p}")
        print()

    if result.conflict_points:
        print("  === CONFLICTING INFORMATION ===\n")
        for p in result.conflict_points:
            print(f"  ! {p}")
        print()

    # Sources table
    print("  === SOURCES ===\n")
    for i, src in enumerate(result.sources, 1):
        title = src.page.title[:50] if src.page else src.search_result.title[:50]
        print(f"  {i}. [{src.credibility_rating}] {title}")
        print(f"     {src.search_result.url}")
    print()

    # Export
    paths = agent.export_report(result, formats=formats)
    if paths:
        print("  === EXPORTED FILES ===\n")
        for fmt, path in paths.items():
            print(f"  {fmt}: {path}")
        print()


def _run_demo(query: str) -> None:
    """Display pre-cached demo results without network access."""
    data = get_demo_result(query)
    if not data:
        print(f"  No demo data for: {query}")
        print(f"  Available: {', '.join(get_demo_queries())}")
        return

    print(f"\n{'='*60}")
    print(f"  Veridex [DEMO] -- {data['query']}")
    print(f"{'='*60}\n")

    print(f"  Sources analyzed: {len(data['sources'])}\n")
    print("  === SUMMARY ===\n")
    print(f"  {data['summary']}\n")

    if data.get("key_sentences"):
        print("  === KEY FINDINGS ===\n")
        for i, s in enumerate(data["key_sentences"][:5], 1):
            print(f"  {i}. {s}")
        print()

    if data.get("key_phrases"):
        print("  === KEY TOPICS ===\n")
        print(f"  {', '.join(data['key_phrases'][:10])}\n")

    if data.get("statistics"):
        print("  === STATISTICS ===\n")
        for stat in data["statistics"][:5]:
            print(f"  - {stat}")
        print()

    if data.get("consensus_points"):
        print("  === SOURCE CONSENSUS ===\n")
        for p in data["consensus_points"]:
            print(f"  + {p}")
        print()

    if data.get("conflict_points"):
        print("  === CONFLICTING INFORMATION ===\n")
        for p in data["conflict_points"]:
            print(f"  ! {p}")
        print()

    print("  === SOURCES ===\n")
    for i, src in enumerate(data["sources"], 1):
        print(f"  {i}. [{src['credibility_rating']}] {src['title'][:50]}")
        print(f"     {src['url']}")
    print()


if __name__ == "__main__":
    main()
