#!/usr/bin/env python3
"""Dynamic Scorer for Research Scanner Skill.

Takes a JSON list of papers and a JSON taxonomy, scores them,
and returns the IDs of papers that meet the minimum score.

Usage:
    python dynamic_scorer.py --papers papers.json --taxonomy taxonomy.json --min-score 3.0
"""

import argparse
import json
import re
import sys
from pathlib import Path


def score_paper(title: str, abstract: str, taxonomy: dict) -> float:
    """Score a paper's relevance against a taxonomy."""
    text = f"{title} {abstract}".lower()
    total_score = 0.0

    for domain, config in taxonomy.items():
        hits = []
        for kw in config.get("keywords", []):
            count = len(re.findall(re.escape(kw.lower()), text))
            if count > 0:
                hits.append({"keyword": kw, "count": count})
        if hits:
            unique_count = len(hits)
            domain_score = config.get("weight", 1.0) * (
                unique_count + sum(min(h["count"], 3) * 0.2 for h in hits)
            )
            total_score += domain_score

    return round(total_score, 2)


def build_taxonomy_from_kg() -> dict:
    """Query the Knowledge Graph to build a dynamic taxonomy."""
    try:
        from agent_utilities.knowledge_graph.core.engine import IntelligenceGraphEngine

        engine = IntelligenceGraphEngine()
    except ImportError:
        print(
            "❌ Failed to import IntelligenceGraphEngine. Is agent-utilities installed?",
            file=sys.stderr,
        )
        sys.exit(1)

    print("🔍 Querying Knowledge Graph for active concepts and codebases...")
    nodes = engine.query(
        "MATCH (n) WHERE n:ConceptNode OR n:CodeNode OR n:ArchitectureNode RETURN n.name as name, labels(n)[0] as type"
    )

    if not nodes:
        print(
            "⚠️ Knowledge Graph is empty or returned no target nodes. Using empty taxonomy."
        )
        return {}

    taxonomy = {}
    for node in nodes:
        name = node.get("name")
        node_type = node.get("type", "ConceptNode")
        if not name:
            continue

        # Create a domain key
        domain_key = name.lower().replace(" ", "_").replace("-", "_")

        # Determine weight based on node type
        weight = 3.0 if node_type == "CodeNode" else 2.0

        # Use the name itself as the primary keyword
        keywords = [name.lower()]

        # Split into individual words if it's a phrase
        words = [w for w in re.split(r"[^a-zA-Z0-9]", name.lower()) if len(w) > 3]
        keywords.extend(words)

        # Remove duplicates
        keywords = list(set(keywords))

        taxonomy[domain_key] = {"weight": weight, "keywords": keywords}

    print(f"✅ Extracted {len(taxonomy)} dynamic focus areas from the KG.")
    return taxonomy


def main():
    parser = argparse.ArgumentParser(
        description="Dynamically score papers against a taxonomy"
    )
    parser.add_argument(
        "--papers",
        required=True,
        help="Path to papers.json (output from get_recent_papers)",
    )
    parser.add_argument(
        "--taxonomy",
        help="Path to taxonomy.json (if omitted, will auto-detect from agent-utilities KG)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=3.0,
        help="Minimum score to consider relevant",
    )
    parser.add_argument(
        "--output",
        default="top_papers.json",
        help="Output JSON path for selected paper IDs",
    )
    args = parser.parse_args()

    papers_path = Path(args.papers)
    if not papers_path.exists():
        print("❌ Missing papers file", file=sys.stderr)
        sys.exit(1)

    taxonomy = {}
    if args.taxonomy:
        taxonomy_path = Path(args.taxonomy)
        if not taxonomy_path.exists():
            print("❌ Missing taxonomy file", file=sys.stderr)
            sys.exit(1)
        try:
            taxonomy = json.loads(taxonomy_path.read_text())
            if "domains" in taxonomy:
                taxonomy = taxonomy["domains"]
        except Exception as e:
            print(f"❌ Error reading taxonomy JSON: {type(e).__name__}", file=sys.stderr)
            sys.exit(1)
    else:
        # Auto-detect from KG if taxonomy not provided
        print("ℹ️ Auto-detecting taxonomy from Knowledge Graph...")
        taxonomy = build_taxonomy_from_kg()

    try:
        papers_data = json.loads(papers_path.read_text())
    except Exception as e:
        print(f"❌ Error reading papers JSON: {type(e).__name__}", file=sys.stderr)
        sys.exit(1)

    # Handle standard MCP output format from get_recent_papers
    papers = (
        papers_data.get("papers", papers_data)
        if isinstance(papers_data, dict)
        else papers_data
    )

    scored_papers = []
    for p in papers:
        title = p.get("title", "")
        abstract = p.get("abstract", "")
        score = score_paper(title, abstract, taxonomy)
        scored_papers.append({"id": p.get("id", ""), "title": title, "score": score})

    scored_papers.sort(key=lambda x: x["score"], reverse=True)

    top_papers = [p for p in scored_papers if p["score"] >= args.min_score]

    print(f"✅ Scored {len(papers)} papers. {len(top_papers)} met the threshold.")
    for p in top_papers:
        print(f"  [{p['score']:5.1f}] {p['title'][:80]}")

    # Output just the IDs to the output file for easy consumption by bulk_download_papers
    output_path = Path(args.output)
    output_path.write_text(json.dumps([p["id"] for p in top_papers], indent=2))
    print(f"\n📁 Saved top paper IDs to {args.output}")


if __name__ == "__main__":
    main()
