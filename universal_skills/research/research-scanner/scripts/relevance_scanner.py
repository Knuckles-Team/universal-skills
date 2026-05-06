#!/usr/bin/env python3
"""Research Scanner — Relevance-Scored Paper Discovery Pipeline.

Fetches papers from academic sources via the ScholarX MCP server,
scores relevance against a configurable taxonomy, filters out junk,
and downloads valuable papers with rate-limiting and retry.

Usage:
    python relevance_scanner.py \
        --query "artificial intelligence" \
        --categories cs.AI,cs.MA,cs.LG \
        --max-results 30 \
        --output-dir /path/to/paper/library

    # With custom taxonomy
    python relevance_scanner.py \
        --query "multi-agent orchestration" \
        --taxonomy /path/to/custom_taxonomy.json \
        --output-dir ./papers

    # With MCP config for ScholarX
    python relevance_scanner.py \
        --query "knowledge graphs" \
        --mcp-config /path/to/mcp_config.json \
        --mcp-server scholarx \
        --output-dir ./papers
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ── Default Taxonomy ────────────────────────────────────────────────────────

DEFAULT_TAXONOMY = {
    "orchestration": {
        "weight": 3.0,
        "keywords": [
            "orchestrat", "multi-agent", "multiagent", "multi agent",
            "agent coordination", "task decomposition", "workflow",
            "agent framework", "agent system", "agentic",
            "tool orchestration", "agent architecture",
        ],
    },
    "knowledge_graph": {
        "weight": 3.0,
        "keywords": [
            "knowledge graph", "ontology", "owl", "semantic web",
            "entity relation", "graph neural", "graph reasoning",
            "node embedding", "link prediction", "triple",
            "knowledge base", "structured knowledge",
        ],
    },
    "planning_reasoning": {
        "weight": 2.5,
        "keywords": [
            "planning", "tree of thought", "chain of thought",
            "reasoning", "deliberat", "test-time compute",
            "inference-time", "search agent", "mcts",
            "monte carlo tree", "beam search", "self-refin",
            "step-by-step", "problem solving",
        ],
    },
    "memory_retrieval": {
        "weight": 2.5,
        "keywords": [
            "memory", "retrieval augmented", "rag", "episodic",
            "experience replay", "context window", "long-context",
            "vector store", "embedding retrieval", "hybrid retrieval",
            "continual learning", "catastrophic forgetting",
        ],
    },
    "tool_use": {
        "weight": 2.0,
        "keywords": [
            "tool use", "tool calling", "function calling",
            "api integration", "mcp", "model context protocol",
            "tool learning", "code generation", "code execution",
            "plugin", "tool augmented",
        ],
    },
    "evaluation_safety": {
        "weight": 2.0,
        "keywords": [
            "evaluation", "benchmark", "red team", "safety",
            "alignment", "guardrail", "adversarial", "robustness",
            "hallucination", "faithfulness", "grounding",
            "reward model", "reward shaping",
        ],
    },
    "swarm_evolution": {
        "weight": 2.0,
        "keywords": [
            "swarm", "evolutionary", "genetic algorithm",
            "population-based", "ant colony", "stigmergy",
            "quorum sensing", "self-organizing", "emergence",
            "collective intelligence", "biomimicry",
        ],
    },
    "llm_architecture": {
        "weight": 1.5,
        "keywords": [
            "transformer", "attention mechanism", "scaling law",
            "mixture of experts", "moe", "fine-tuning", "sft",
            "reinforcement learning from", "rlhf", "dpo",
            "distillation", "quantization", "efficient inference",
        ],
    },
    "human_ai": {
        "weight": 1.0,
        "keywords": [
            "human-in-the-loop", "human-ai", "collaborative",
            "interactive", "conversational", "dialogue",
            "user interface", "decision support",
        ],
    },
}

# ── Rate Limiting Constants ─────────────────────────────────────────────────

DOWNLOAD_DELAY = 3.5  # seconds between downloads (arXiv: 1 req/3s + margin)
MAX_RETRIES = 3
RETRY_BACKOFF = [5, 10, 20]


# ── Scoring Engine ──────────────────────────────────────────────────────────

def score_paper(title: str, abstract: str, taxonomy: dict) -> dict:
    """Score a paper's relevance against the taxonomy.

    Returns:
        dict with total_score, domain_hits, domains_matched, verdict
    """
    text = f"{title} {abstract}".lower()
    total_score = 0.0
    domain_hits = {}

    for domain, config in taxonomy.items():
        hits = []
        for kw in config["keywords"]:
            count = len(re.findall(re.escape(kw.lower()), text))
            if count > 0:
                hits.append({"keyword": kw, "count": count})
        if hits:
            unique_count = len(hits)
            domain_score = config["weight"] * (
                unique_count + sum(min(h["count"], 3) * 0.2 for h in hits)
            )
            total_score += domain_score
            domain_hits[domain] = {
                "keywords": hits,
                "domain_score": round(domain_score, 2),
            }

    if total_score >= 3.0:
        verdict = "relevant"
    elif total_score >= 1.0:
        verdict = "marginal"
    else:
        verdict = "irrelevant"

    return {
        "total_score": round(total_score, 2),
        "domain_hits": domain_hits,
        "domains_matched": len(domain_hits),
        "verdict": verdict,
    }


# ── MCP Client Helpers ──────────────────────────────────────────────────────

def find_mcp_client_script() -> str | None:
    """Find the mcp_client.py script in known locations."""
    candidates = [
        Path(__file__).parent.parent.parent.parent / "integration" / "mcp-client" / "scripts" / "mcp_client.py",
        Path.home() / ".gemini" / "antigravity" / "skills" / "mcp-client" / "scripts" / "mcp_client.py",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def call_mcp_tool(
    mcp_config: str,
    server: str,
    tool_name: str,
    tool_args: dict,
    timeout: int = 60,
) -> dict | None:
    """Call a ScholarX MCP tool via the mcp-client script.

    Returns parsed JSON result or None on failure.
    """
    mcp_script = find_mcp_client_script()
    if not mcp_script:
        print("  ⚠️  mcp_client.py not found, falling back to direct API", file=sys.stderr)
        return None

    cmd = [
        sys.executable, mcp_script,
        "--config", mcp_config,
        "--server", server,
        "--action", "call-mcp-tool",
        "--tool-name", tool_name,
        "--tool-args", json.dumps(tool_args),
        "--timeout", str(timeout),
    ]

    try:
        result = subprocess.run(  # nosec B603
            cmd, capture_output=True, text=True, timeout=timeout + 30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        print(f"  ⚠️  MCP call failed: {e}", file=sys.stderr)

    return None


# ── Direct API Fallback ─────────────────────────────────────────────────────

async def fetch_papers_direct(
    query: str,
    categories: list[str],
    max_results: int,
    sort_by: str = "date",
) -> list[dict]:
    """Fetch papers using ScholarX Python API directly (fallback)."""
    try:
        from scholarx.api_client import ScholarXClient
        from scholarx.models import PaperSource, SearchQuery

        client = ScholarXClient(sources=[PaperSource.ARXIV])
        sq = SearchQuery(
            query=query,
            sources=[PaperSource.ARXIV],
            categories=categories,
            max_results=max_results,
            sort_by=sort_by,
        )
        result = await client.search(sq)
        return [p.model_dump(exclude={"normalized_title", "normalized_authors"}) for p in result.papers]
    except ImportError:
        print("ERROR: ScholarX not installed and MCP not available", file=sys.stderr)
        return []


async def download_paper_direct(paper_data: dict, storage_dir: str) -> str | None:
    """Download a paper PDF using ScholarX API directly (fallback)."""
    try:
        from scholarx.api_client import ScholarXClient
        from scholarx.models import Paper, PaperSource

        client = ScholarXClient(
            sources=[PaperSource.ARXIV],
            storage_dir=storage_dir,
        )
        paper = Paper(**paper_data)
        return await client.download_paper(paper)
    except Exception as e:
        print(f"  ⚠️  Direct download failed: {e}", file=sys.stderr)
        return None


# ── Synergy Report Generator ────────────────────────────────────────────────

def generate_synergy_report(
    output_dir: Path,
    scored: list[dict],
    accepted: list[dict],
) -> Path:
    """Generate a consolidated synergy_report.md from scored papers.

    Groups synergies by target domain and produces a readable markdown report
    with per-paper breakdowns and a domain integration roadmap.
    """
    domain_agg: dict[str, list[dict]] = defaultdict(list)
    lines = [
        "# Research Synergy Report",
        "",
        f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Papers Fetched**: {len(scored)}",
        f"**Papers Accepted**: {len(accepted)}",
        "",
        "## Relevance Ranking",
        "",
        "| # | Score | Verdict | Domains | Title |",
        "|---|-------|---------|---------|-------|",
    ]

    for i, sp in enumerate(accepted, 1):
        p = sp["paper"]
        s = sp["score"]
        domains = ", ".join(s["domain_hits"].keys()) if s["domain_hits"] else "—"
        icon = {"relevant": "✅", "marginal": "🟡", "irrelevant": "❌"}[s["verdict"]]
        lines.append(
            f"| {i} | {s['total_score']} | {icon} {s['verdict']} | {domains} | {p['title'][:70]} |"
        )
        # Collect domain hits for aggregation
        for domain, info in s["domain_hits"].items():
            for kw in info.get("keywords", []):
                domain_agg[domain].append({
                    "paper": p["title"],
                    "keyword": kw["keyword"],
                    "count": kw["count"],
                    "domain_score": info["domain_score"],
                })

    # Domain summary
    lines += [
        "",
        "## Synergies by Domain",
        "",
        "| Domain | Papers | Total Keywords | Aggregate Score |",
        "|--------|--------|---------------|-----------------|",
    ]
    for domain in sorted(domain_agg.keys(), key=lambda d: len(domain_agg[d]), reverse=True):
        entries = domain_agg[domain]
        papers = len(set(e["paper"] for e in entries))
        kws = len(entries)
        total_score = sum(e["domain_score"] for e in entries) / max(papers, 1)
        lines.append(f"| `{domain}` | {papers} | {kws} | {total_score:.1f} avg |")

    # Domain deep dive
    lines += ["", "## Domain Integration Roadmap", ""]
    for domain in sorted(domain_agg.keys(), key=lambda d: len(domain_agg[d]), reverse=True):
        entries = domain_agg[domain]
        paper_groups: dict[str, list[str]] = defaultdict(list)
        for e in entries:
            paper_groups[e["paper"]].append(e["keyword"])
        lines.append(f"### `{domain}` ({len(paper_groups)} papers)")
        lines.append("")
        for paper, kws in paper_groups.items():
            lines.append(f"- **{paper[:70]}** — keywords: {', '.join(kws)}")
        lines.append("")

    # Filtered papers
    filtered = [sp for sp in scored if sp["score"]["verdict"] == "irrelevant"]
    if filtered:
        lines += ["## Filtered Papers (No Value)", ""]
        for sp in filtered:
            lines.append(f"- ❌ [{sp['score']['total_score']}] {sp['paper']['title']}")
        lines.append("")

    report_path = output_dir / "synergy_report.md"
    report_path.write_text("\n".join(lines))
    return report_path


# ── Main Pipeline ───────────────────────────────────────────────────────────

async def run_pipeline(args: argparse.Namespace) -> dict:
    """Execute the full research scanning pipeline."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir = output_dir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    # Load taxonomy
    taxonomy = DEFAULT_TAXONOMY
    if args.taxonomy:
        tax_path = Path(args.taxonomy)
        if tax_path.exists():
            tax_data = json.loads(tax_path.read_text())
            taxonomy = tax_data.get("domains", tax_data)
            print(f"📋 Loaded custom taxonomy: {len(taxonomy)} domains")

    categories = [c.strip() for c in args.categories.split(",")]

    print("=" * 70)
    print("Research Scanner — Relevance-Scored Paper Pipeline")
    print("=" * 70)

    # ── Phase 1: Fetch papers ────────────────────────────────────────────
    print(f"\n🔍 Fetching {args.max_results} papers...")
    print(f"   Query: {args.query}")
    print(f"   Categories: {', '.join(categories)}")

    papers_data = []

    # Try MCP first, fall back to direct API
    if args.mcp_config:
        mcp_result = call_mcp_tool(
            args.mcp_config, args.mcp_server,
            "search_papers",
            {
                "query": args.query,
                "sources": "arxiv",
                "categories": ",".join(categories),
                "max_results": args.max_results,
                "sort_by": "date",
            },
            timeout=args.timeout,
        )
        if mcp_result and "papers" in mcp_result:
            papers_data = mcp_result["papers"]
            print(f"   📡 Fetched via MCP: {len(papers_data)} papers")

    if not papers_data:
        print("   📡 Using direct API...")
        papers_data = await fetch_papers_direct(
            args.query, categories, args.max_results,
        )
        print(f"   Retrieved: {len(papers_data)} papers")

    if not papers_data:
        print("\n❌ No papers found. Exiting.")
        return {"status": "no_papers", "count": 0}

    # ── Phase 2: Score relevance ─────────────────────────────────────────
    print(f"\n📊 Scoring relevance against {len(taxonomy)} domains...\n")
    scored = []
    for pd in papers_data:
        title = pd.get("title", "")
        abstract = pd.get("abstract", "")
        score = score_paper(title, abstract, taxonomy)
        scored.append({"paper": pd, "score": score})

    scored.sort(key=lambda x: x["score"]["total_score"], reverse=True)

    # ── Phase 3: Filter ──────────────────────────────────────────────────
    relevant = [s for s in scored if s["score"]["verdict"] == "relevant"]
    marginal = [s for s in scored if s["score"]["verdict"] == "marginal"]
    irrelevant = [s for s in scored if s["score"]["verdict"] == "irrelevant"]
    accepted = relevant + marginal

    for sp in scored:
        p = sp["paper"]
        s = sp["score"]
        icon = {"relevant": "✅", "marginal": "🟡", "irrelevant": "❌"}[s["verdict"]]
        print(f"  {icon} [{s['total_score']:5.1f}] {p['title'][:80]}")
        if s["domain_hits"]:
            domains = ", ".join(s["domain_hits"].keys())
            print(f"         Domains: {domains}")

    print(f"\n{'─' * 70}")
    print(f"  ✅ Relevant:   {len(relevant)} papers (score ≥ 3.0)")
    print(f"  🟡 Marginal:   {len(marginal)} papers (score 1.0-2.9)")
    print(f"  ❌ Irrelevant: {len(irrelevant)} papers (score < 1.0)")
    print(f"  📥 Accepting {len(accepted)} papers (filtering out {len(irrelevant)} junk)")

    # ── Save outputs ─────────────────────────────────────────────────────

    # Scoring summary
    scoring_summary = {
        "total_fetched": len(scored),
        "accepted": len(accepted),
        "filtered_out": len(irrelevant),
        "query": args.query,
        "categories": categories,
        "papers": [
            {
                "title": sp["paper"]["title"],
                "id": sp["paper"].get("id", ""),
                "score": sp["score"]["total_score"],
                "verdict": sp["score"]["verdict"],
                "domains_matched": sp["score"]["domains_matched"],
                "domain_hits": {
                    d: v["domain_score"]
                    for d, v in sp["score"]["domain_hits"].items()
                },
            }
            for sp in scored
        ],
    }
    (output_dir / "relevance_scores.json").write_text(
        json.dumps(scoring_summary, indent=2)
    )

    # Paper markdowns
    for i, sp in enumerate(accepted, 1):
        paper = sp["paper"]
        score = sp["score"]
        content = f"""# {paper['title']}

**Relevance Score:** {score['total_score']} ({score['verdict']})
**Domains Matched:** {', '.join(score['domain_hits'].keys()) if score['domain_hits'] else 'none'}
**Source:** {paper.get('source', 'unknown')}
**ID:** {paper.get('id', 'unknown')}
**Published:** {paper.get('published_date', 'unknown')}
**URL:** {paper.get('url', '')}
**DOI:** {paper.get('doi') or 'N/A'}
**Categories:** {', '.join(paper.get('categories', []))}

## Authors
{chr(10).join(f'- {a}' for a in paper.get('authors', []))}

## Abstract
{paper.get('abstract', 'N/A')}

## Relevance Analysis
{json.dumps(score['domain_hits'], indent=2)}
"""
        (output_dir / f"paper_{i:02d}.md").write_text(content)

    # Metadata
    accepted_meta = [sp["paper"] for sp in accepted]
    (output_dir / "papers_metadata.json").write_text(
        json.dumps(accepted_meta, indent=2, default=str)
    )

    # ── Phase 4: Download PDFs with rate limiting ────────────────────────
    print(f"\n📥 Downloading {len(accepted)} PDFs (rate limited: {DOWNLOAD_DELAY}s between requests)...")
    downloaded = 0
    failed = []

    for i, sp in enumerate(accepted, 1):
        paper = sp["paper"]
        pdf_url = paper.get("pdf_url", "")
        if not pdf_url:
            print(f"  ⚠️  [{i}/{len(accepted)}] No PDF URL: {paper['title'][:50]}...")
            continue

        # Rate limit
        if i > 1:
            await asyncio.sleep(DOWNLOAD_DELAY)

        for attempt in range(MAX_RETRIES):
            try:
                if attempt > 0:
                    await asyncio.sleep(RETRY_BACKOFF[attempt])

                path = await download_paper_direct(paper, str(pdf_dir))
                if path:
                    downloaded += 1
                    print(f"  ✅ [{i}/{len(accepted)}] {paper['title'][:55]}...")
                    break
                else:
                    print(f"  ⚠️  [{i}/{len(accepted)}] Download returned None")
                    break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"  🔄 [{i}/{len(accepted)}] Retry {attempt + 1}: {e}")
                else:
                    print(f"  ❌ [{i}/{len(accepted)}] Failed: {e}")
                    failed.append(paper["title"])

    # ── Phase 5: Generate synergy report ───────────────────────────────────
    report_path = generate_synergy_report(output_dir, scored, accepted)
    print(f"\n📊 Synergy report: {report_path}")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"✅ Research Scanner Complete!")
    print(f"   Papers fetched:  {len(scored)}")
    print(f"   Papers accepted: {len(accepted)} (relevant + marginal)")
    print(f"   Papers filtered: {len(irrelevant)} (zero value)")
    print(f"   PDFs downloaded: {downloaded}")
    if failed:
        print(f"   Failed downloads: {len(failed)}")
    print(f"   Output dir:      {output_dir}")
    print(f"   Reports:         relevance_scores.json, synergy_report.md")
    print(f"{'=' * 70}")

    return {
        "status": "success",
        "total_fetched": len(scored),
        "accepted": len(accepted),
        "filtered_out": len(irrelevant),
        "downloaded": downloaded,
        "failed": len(failed),
        "output_dir": str(output_dir),
        "synergy_report": str(report_path),
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Research Scanner — relevance-scored paper discovery"
    )
    parser.add_argument("--query", required=True, help="Search query string")
    parser.add_argument(
        "--categories", default="cs.AI,cs.MA,cs.LG",
        help="Comma-separated arXiv categories (default: cs.AI,cs.MA,cs.LG)",
    )
    parser.add_argument(
        "--max-results", type=int, default=30,
        help="Maximum papers to fetch (default: 30)",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory to save papers and reports",
    )
    parser.add_argument(
        "--taxonomy", default=None,
        help="Path to custom relevance_taxonomy.json",
    )
    parser.add_argument(
        "--mcp-config", default=None,
        help="Path to ScholarX MCP config (enables MCP mode)",
    )
    parser.add_argument(
        "--mcp-server", default="scholarx",
        help="Server name in MCP config (default: scholarx)",
    )
    parser.add_argument(
        "--timeout", type=int, default=60,
        help="MCP call timeout in seconds (default: 60)",
    )

    args = parser.parse_args()
    result = asyncio.run(run_pipeline(args))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
