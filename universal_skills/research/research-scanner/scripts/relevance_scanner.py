#!/usr/bin/env python3
"""Research Scanner — Unified CLI for Paper Discovery and Scoring.

Thin CLI wrapper around the ScholarX scanner library. Supports two modes:

1. **daily** — Fetch today's papers from arXiv RSS, score, filter, download
2. **search** — Query-based paper search with relevance scoring

All heavy lifting is delegated to ``scholarx.scanner.RelevanceScanner``.

Usage:
    # Daily RSS scan
    python relevance_scanner.py --mode daily \
        --categories cs.AI \
        --output-dir scholarx_papers/daily_2026-05-08

    # Fetch by specific IDs
    python relevance_scanner.py --mode fetch \
        --paper-ids "2605.05242,2605.06177" \
        --output-dir scholarx_papers/fetch_results

    # Query-based search
    python relevance_scanner.py --mode search \
        --query "multi-agent orchestration" \
        --categories cs.AI,cs.MA,cs.LG \
        --max-results 30 \
        --output-dir scholarx_papers/query_results

    # With custom taxonomy
    python relevance_scanner.py --mode daily \\
        --categories cs.AI,cs.MA \\
        --taxonomy /path/to/custom_taxonomy.json \\
        --output-dir ./papers
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path


def _load_taxonomy(taxonomy_path: str | None) -> dict | None:
    """Load a custom taxonomy from JSON file."""
    if not taxonomy_path:
        return None
    tax_path = Path(taxonomy_path)
    if not tax_path.exists():
        print(f"⚠️  Taxonomy file not found: {taxonomy_path}", file=sys.stderr)
        return None
    tax_data = json.loads(tax_path.read_text())
    taxonomy = tax_data.get("domains", tax_data)
    print(f"📋 Loaded custom taxonomy: {len(taxonomy)} domains")
    return taxonomy


async def run_daily(args: argparse.Namespace) -> dict:
    """Execute the daily RSS scanning pipeline."""
    from scholarx.scanner import RelevanceScanner

    taxonomy = _load_taxonomy(args.taxonomy)
    categories = [c.strip() for c in args.categories.split(",")]

    scanner = RelevanceScanner(
        taxonomy=taxonomy,
        library_dir=args.library_dir or None,
        min_download_score=args.min_score,
    )

    print("=" * 70)
    print("Research Scanner — Daily RSS Pipeline")
    print("=" * 70)
    print(f"\n🔍 Categories: {', '.join(categories)}")
    print(f"   Output:     {args.output_dir}")

    result = await scanner.scan_daily(
        categories=categories,
        output_dir=args.output_dir,
        download_pdfs=not args.no_download,
    )

    # Print results
    _print_results(result)
    return result.model_dump(exclude={"scored_papers"})


async def run_search(args: argparse.Namespace) -> dict:
    """Execute the query-based search pipeline."""
    from scholarx.scanner import RelevanceScanner

    if not args.query:
        print("❌ --query is required for search mode", file=sys.stderr)
        return {"status": "error", "message": "Missing --query"}

    taxonomy = _load_taxonomy(args.taxonomy)
    categories = [c.strip() for c in args.categories.split(",")]

    scanner = RelevanceScanner(
        taxonomy=taxonomy,
        min_download_score=args.min_score,
    )

    print("=" * 70)
    print("Research Scanner — Query-Based Search")
    print("=" * 70)
    print(f"\n🔍 Query:      {args.query}")
    print(f"   Categories: {', '.join(categories)}")
    print(f"   Max results: {args.max_results}")

    result = await scanner.scan_query(
        query=args.query,
        categories=categories,
        max_results=args.max_results,
        output_dir=args.output_dir,
        download_pdfs=not args.no_download,
    )

    _print_results(result)
    return result.model_dump(exclude={"scored_papers"})


async def run_fetch(args: argparse.Namespace) -> dict:
    """Execute the ID-based fetch pipeline."""
    from scholarx.scanner import RelevanceScanner

    if not getattr(args, 'paper_ids', None):
        print("❌ --paper-ids is required for fetch mode", file=sys.stderr)
        return {"status": "error", "message": "Missing --paper-ids"}

    taxonomy = _load_taxonomy(args.taxonomy)
    paper_ids = [pid.strip() for pid in args.paper_ids.split(",")]

    scanner = RelevanceScanner(
        taxonomy=taxonomy,
    )

    print("=" * 70)
    print("Research Scanner — Paper ID Fetch Pipeline")
    print("=" * 70)
    print(f"\n🔍 Paper IDs: {', '.join(paper_ids)}")
    print(f"   Output:    {args.output_dir}")

    result = await scanner.scan_ids(
        paper_ids=paper_ids,
        output_dir=args.output_dir,
        download_pdfs=not args.no_download,
    )

    _print_results(result)
    return result.model_dump(exclude={"scored_papers"})


def _print_results(result) -> None:
    """Print scan results in a human-readable format."""
    s = result.stats

    # Print scored papers
    if result.scored_papers:
        print(f"\n📊 Scoring results ({len(result.scored_papers)} papers):\n")
        for sp in result.scored_papers:
            p = sp.paper
            sc = sp.score
            icon = {"relevant": "✅", "marginal": "🟡", "irrelevant": "❌"}[sc.verdict]
            atype = p.get("announce_type", "?")
            print(
                f"  {icon} [{sc.total_score:5.1f}] [{atype:5s}] {p.get('title', '')[:75]}"
            )
            if sc.domain_hits:
                domains = ", ".join(sc.domain_hits.keys())
                print(f"         Domains: {domains}")

    print(f"\n{'─' * 70}")
    print(f"  ✅ Relevant:   {s.relevant_count} papers (score ≥ 3.0)")
    print(f"  🟡 Marginal:   {s.marginal_count} papers (score 1.0-2.9)")
    print(f"  ❌ Irrelevant: {s.filtered_count} papers (score < 1.0)")
    print(f"  📥 Downloaded: {s.downloaded_count} PDFs")
    if s.deduplicated_count:
        print(f"  🔄 Deduped:    {s.deduplicated_count} already in library")
    if s.failed_count:
        print(f"  ⚠️  Failed:    {s.failed_count} downloads")
    print(f"\n  📊 Report:     {result.synergy_report_path}")
    print(f"  📁 Output:     {result.output_dir}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="Research Scanner — paper discovery and relevance scoring"
    )
    parser.add_argument(
        "--mode",
        choices=["daily", "search", "fetch"],
        default="daily",
        help="Scanning mode: 'daily' for RSS feed, 'search' for query-based, 'fetch' for specific IDs (default: daily)",
    )
    parser.add_argument(
        "--query",
        default="",
        help="Search query string (required for search mode)",
    )
    parser.add_argument(
        "--paper-ids",
        default="",
        help="Comma-separated paper IDs to fetch (required for fetch mode)",
    )
    parser.add_argument(
        "--categories",
        default="cs.AI",
        help="Comma-separated arXiv categories (default: cs.AI)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=30,
        help="Maximum papers to fetch in search mode (default: 30)",
    )
    parser.add_argument(
        "--output-dir",
        default=f"scholarx_papers/daily_{datetime.now().strftime('%Y-%m-%d')}",
        help="Directory to save papers and reports",
    )
    parser.add_argument(
        "--library-dir",
        default="scholarx_papers",
        help="Existing paper library for deduplication (daily mode)",
    )
    parser.add_argument(
        "--taxonomy",
        default=None,
        help="Path to custom relevance_taxonomy.json",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=3.0,
        help="Minimum score for PDF downloads (default: 3.0)",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Skip PDF downloads",
    )

    args = parser.parse_args()

    if args.mode == "daily":
        result = asyncio.run(run_daily(args))
    elif args.mode == "search":
        result = asyncio.run(run_search(args))
    else:
        result = asyncio.run(run_fetch(args))

    print("\n" + json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
