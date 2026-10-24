#!/usr/bin/env python3
"""CA-011: Concept-seeded cross-reference — map research papers to concept IDs.

Queries the Knowledge Graph for each concept ID in the agent-utilities
concept registry, finds relevant Article (paper) nodes via semantic search,
and runs innovation extraction against each match.

Usage:
    # From KG (requires agent-utilities-kg MCP server running):
    python concept_cross_reference.py --kg

    # From a concept_map.md file:
    python concept_cross_reference.py --concept-map /path/to/concept_map.md

    # Filter to specific pillars:
    python concept_cross_reference.py --kg --pillars ORCH KG

    # Adjust similarity threshold:
    python concept_cross_reference.py --kg --threshold 0.65

    # Output to file:
    python concept_cross_reference.py --kg --output report.json

    # Batched processing (for 200+ concepts):
    python concept_cross_reference.py --kg --batch-size 20 --output report.json

    # Resume from a partial run:
    python concept_cross_reference.py --kg --resume partial_report.json --output report.json

CONCEPT:CA-011 — Concept Cross-Reference Engine
"""

import json
import re
import sys
import time
from pathlib import Path

try:
    import networkx as nx
except ImportError:
    nx = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Concept Map Parser
# ---------------------------------------------------------------------------

# Regex to pull concept rows from the markdown table format used in concept_map.md
# Expected format: | `ORCH-1.0` | Intelligence Graph Core | ... |
_CONCEPT_ROW_RE = re.compile(
    r"\|\s*`([A-Z]+-\d+\.\d+)`\s*\|\s*([^|]+?)\s*\|",
    re.MULTILINE,
)

# Pillar name mapping from prefix
PILLAR_NAMES = {
    "ORCH": "Graph Orchestration Engine",
    "KG": "Epistemic Knowledge Graph",
    "AHE": "Agentic Harness Engineering",
    "ECO": "Ecosystem & Peripherals",
    "OS": "Agent OS Infrastructure",
}


def parse_concept_map_file(path: Path) -> list[dict]:
    """Parse a concept_map.md file and extract concept IDs with names."""
    content = path.read_text(encoding="utf-8")
    concepts = []
    for match in _CONCEPT_ROW_RE.finditer(content):
        concept_id = match.group(1)
        concept_name = match.group(2).strip()
        prefix = concept_id.split("-")[0]
        concepts.append(
            {
                "concept_id": concept_id,
                "name": concept_name,
                "pillar": prefix,
                "pillar_name": PILLAR_NAMES.get(prefix, prefix),
            }
        )
    return concepts


def parse_concepts_from_kg(kg_results: list[dict]) -> list[dict]:
    """Parse concept nodes returned from a KG query."""
    concepts = []
    for row in kg_results:
        cid = row.get("concept_id", row.get("id", ""))
        name = row.get("name", row.get("title", cid))
        prefix = cid.split("-")[0] if "-" in cid else "UNKNOWN"
        concepts.append(
            {
                "concept_id": cid,
                "name": name,
                "pillar": prefix,
                "pillar_name": PILLAR_NAMES.get(prefix, prefix),
            }
        )
    return concepts


# ---------------------------------------------------------------------------
# Innovation Extraction (inline, borrowed from extract_innovations.py)
# ---------------------------------------------------------------------------

BIOMIMICRY_KEYWORDS = {
    "swarm": {"analogy": "multi-agent coordination", "domain": "orchestration"},
    "colony": {"analogy": "distributed task allocation", "domain": "scheduling"},
    "pheromone": {
        "analogy": "stigmergic communication channels",
        "domain": "signal_boards",
    },
    "neural": {"analogy": "adaptive model routing", "domain": "model_selection"},
    "immune": {
        "analogy": "anomaly detection and self-healing",
        "domain": "circuit_breakers",
    },
    "evolution": {
        "analogy": "genetic algorithm optimization",
        "domain": "prompt_evolution",
    },
    "mutation": {"analogy": "parametric exploration", "domain": "variant_pool"},
    "symbiosis": {
        "analogy": "plugin ecosystem composition",
        "domain": "mcp_composition",
    },
    "metamorphosis": {
        "analogy": "schema evolution and migration",
        "domain": "schema_packs",
    },
    "quorum": {"analogy": "distributed consensus thresholds", "domain": "bft_voting"},
    "mycelium": {"analogy": "knowledge graph topology", "domain": "kg_routing"},
    "plasticity": {"analogy": "continual learning without forgetting", "domain": "ewc"},
    "homeostasis": {
        "analogy": "resource equilibrium maintenance",
        "domain": "cost_governors",
    },
    "emergent": {
        "analogy": "complex behavior from simple rules",
        "domain": "swarm_presets",
    },
    "stigmergy": {
        "analogy": "indirect coordination via environment",
        "domain": "signal_boards",
    },
}

TECH_INNOVATION_KEYWORDS = {
    "attention": {
        "analogy": "context-aware retrieval weighting",
        "domain": "hybrid_retriever",
    },
    "transformer": {
        "analogy": "parallel sequence processing",
        "domain": "batch_processing",
    },
    "embedding": {
        "analogy": "semantic vector representation",
        "domain": "knowledge_graph",
    },
    "reinforcement": {
        "analogy": "reward-driven routing optimization",
        "domain": "confidence_gating",
    },
    "chain-of-thought": {"analogy": "rationale persistence", "domain": "quiet_star"},
    "tree search": {"analogy": "MCTS planning fallback", "domain": "lats"},
    "distillation": {
        "analogy": "knowledge compression",
        "domain": "trace_distillation",
    },
    "consensus": {"analogy": "multi-agent agreement", "domain": "bft"},
    "zero-shot": {"analogy": "inductive generalization", "domain": "encpi"},
    "few-shot": {"analogy": "rapid domain adaptation", "domain": "experience_nodes"},
    "curriculum": {
        "analogy": "progressive complexity scheduling",
        "domain": "horizon_curriculum",
    },
    "credit assignment": {
        "analogy": "multi-step reward attribution",
        "domain": "reward_decomposition",
    },
    "reward shaping": {
        "analogy": "step-level outcome signals",
        "domain": "reward_decomposition",
    },
    "horizon reduction": {
        "analogy": "macro-action composition",
        "domain": "horizon_curriculum",
    },
    "macro action": {
        "analogy": "composite multi-step primitives",
        "domain": "horizon_curriculum",
    },
    "subgoal": {
        "analogy": "intermediate milestone decomposition",
        "domain": "task_decomposition",
    },
    "knowledge graph": {"analogy": "structured relational memory", "domain": "kg"},
    "ontology": {"analogy": "formal domain modeling", "domain": "owl_reasoning"},
    "owl": {
        "analogy": "web ontology language for semantic reasoning",
        "domain": "owl_bridge",
    },
    "sparql": {"analogy": "structured graph query language", "domain": "kg_query"},
    "hypergraph": {"analogy": "n-ary relationship modeling", "domain": "hyperedges"},
    "topology": {"analogy": "structural graph analysis", "domain": "partitioning"},
    "vector index": {"analogy": "ANN search structure", "domain": "vector_retrieval"},
    "graph embedding": {"analogy": "structural position encoding", "domain": "encpi"},
    "community detection": {
        "analogy": "cluster discovery in graphs",
        "domain": "graph_clustering",
    },
    "centrality": {"analogy": "node importance ranking", "domain": "graph_analysis"},
    "hierarchical": {
        "analogy": "multi-level abstraction layering",
        "domain": "hierarchical_planning",
    },
    "composability": {
        "analogy": "modular building-block assembly",
        "domain": "mcp_composition",
    },
    "plugin": {
        "analogy": "hot-swappable capability extension",
        "domain": "plugin_registry",
    },
    "middleware": {
        "analogy": "cross-cutting concern interception",
        "domain": "middleware",
    },
    "transitive": {
        "analogy": "inferred multi-hop relationships",
        "domain": "owl_transitivity",
    },
    "inference": {
        "analogy": "derived knowledge from assertions",
        "domain": "owl_reasoning",
    },
    "retrieval": {
        "analogy": "context-aware document fetching",
        "domain": "hybrid_retriever",
    },
    "rag": {"analogy": "retrieval-augmented generation", "domain": "hybrid_retriever"},
    "multi-agent": {
        "analogy": "coordinated specialist teams",
        "domain": "orchestration",
    },
    "orchestration": {
        "analogy": "workflow coordination engine",
        "domain": "orchestration",
    },
    "planning": {
        "analogy": "task decomposition and scheduling",
        "domain": "htn_planning",
    },
    "tool use": {
        "analogy": "dynamic capability invocation",
        "domain": "tool_interface",
    },
    "mcp": {"analogy": "model context protocol integration", "domain": "mcp_factory"},
    "safety": {
        "analogy": "guardrails and constraint enforcement",
        "domain": "guardrails",
    },
    "guardrail": {"analogy": "safety boundary enforcement", "domain": "guardrails"},
    "evaluation": {
        "analogy": "quality assessment framework",
        "domain": "evaluation_engine",
    },
    "benchmark": {
        "analogy": "standardized performance testing",
        "domain": "evaluation_engine",
    },
    "telemetry": {"analogy": "runtime observability signals", "domain": "telemetry"},
    "observability": {"analogy": "system state transparency", "domain": "telemetry"},
    "security": {"analogy": "threat defense mechanisms", "domain": "security"},
    "authentication": {"analogy": "identity verification", "domain": "security"},
    "scheduling": {
        "analogy": "resource allocation optimization",
        "domain": "cognitive_scheduler",
    },
    "memory": {"analogy": "persistent experience storage", "domain": "tiered_memory"},
    "consolidation": {
        "analogy": "memory compression and retention",
        "domain": "memory_consolidation",
    },
    "context window": {
        "analogy": "adaptive context management",
        "domain": "context_management",
    },
    "red team": {
        "analogy": "adversarial testing framework",
        "domain": "evaluation_engine",
    },
    "federated": {
        "analogy": "distributed graph querying",
        "domain": "external_federation",
    },
}

_INNOVATION_SIGNALS = [
    "novel",
    "new",
    "propose",
    "introduce",
    "demonstrate",
    "improve",
    "outperform",
    "achieve",
    "enable",
    "first",
    "state-of-the-art",
    "sota",
    "surpass",
    "advance",
]


def extract_innovations_from_text(content: str, concept_id: str = "") -> dict:
    """Extract innovation signals from text, optionally tagged to a concept."""
    content_lower = content.lower()
    biomimicry_hits = []
    tech_hits = []

    for keyword, info in BIOMIMICRY_KEYWORDS.items():
        count = content_lower.count(keyword)
        if count > 0:
            biomimicry_hits.append(
                {
                    "keyword": keyword,
                    "count": count,
                    "analogy": info["analogy"],
                    "target_domain": info["domain"],
                }
            )

    for keyword, info in TECH_INNOVATION_KEYWORDS.items():
        count = content_lower.count(keyword)
        if count > 0:
            tech_hits.append(
                {
                    "keyword": keyword,
                    "count": count,
                    "analogy": info["analogy"],
                    "target_domain": info["domain"],
                }
            )

    # Extract key claims
    claims = []
    sentences = re.split(r"[.!?]\s+", content)
    for sent in sentences:
        if any(sig in sent.lower() for sig in _INNOVATION_SIGNALS):
            words = sent.split()
            if 5 < len(words) < 50:
                claims.append(sent.strip())
    claims = claims[:10]

    result = {
        "biomimicry_signals": sorted(biomimicry_hits, key=lambda x: -x["count"]),
        "tech_signals": sorted(tech_hits, key=lambda x: -x["count"]),
        "innovation_claims": claims,
    }
    if concept_id:
        result["concept_id"] = concept_id
    return result


# ---------------------------------------------------------------------------
# Concept × Paper Cross-Reference
# ---------------------------------------------------------------------------


def cross_reference_concept(
    concept: dict,
    article_chunks: list[dict],
    threshold: float = 0.60,
) -> dict:
    """Cross-reference a single concept against Article chunks.

    Args:
        concept: Dict with concept_id, name, pillar, pillar_name.
        article_chunks: List of Article node dicts from KG search, each with
            'content', 'score', 'id', 'metadata', 'target_path'.
        threshold: Minimum similarity score to include.

    Returns:
        Dict with concept info, matched papers, extracted innovations.
    """
    relevant_chunks = [c for c in article_chunks if c.get("score", 0) >= threshold]

    if not relevant_chunks:
        return {
            **concept,
            "match_count": 0,
            "paper_matches": [],
            "innovations": [],
            "total_innovation_signals": 0,
        }

    # Group chunks by source paper (target_path)
    paper_groups: dict[str, list[dict]] = {}
    for chunk in relevant_chunks:
        paper_path = chunk.get(
            "target_path", chunk.get("metadata", {}).get("file_path", "unknown")
        )
        if paper_path not in paper_groups:
            paper_groups[paper_path] = []
        paper_groups[paper_path].append(chunk)

    paper_matches = []
    all_innovations: list[dict] = []

    for paper_path, chunks in paper_groups.items():
        # Combine chunk content for innovation extraction
        combined_content = "\n".join(c.get("content", "") for c in chunks)
        avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
        max_score = max(c.get("score", 0) for c in chunks)

        innovations = extract_innovations_from_text(
            combined_content, concept["concept_id"]
        )
        signal_count = len(innovations["biomimicry_signals"]) + len(
            innovations["tech_signals"]
        )

        paper_match = {
            "paper_path": paper_path,
            "paper_name": Path(paper_path).stem
            if paper_path != "unknown"
            else "unknown",
            "chunk_count": len(chunks),
            "avg_similarity": round(avg_score, 4),
            "max_similarity": round(max_score, 4),
            "innovation_signal_count": signal_count,
            "top_claims": innovations["innovation_claims"][:3],
            "top_tech_signals": innovations["tech_signals"][:5],
            "top_biomimicry_signals": innovations["biomimicry_signals"][:3],
        }
        paper_matches.append(paper_match)
        all_innovations.append(innovations)

    # Sort by relevance (max_similarity * signal_count)
    paper_matches.sort(
        key=lambda x: x["max_similarity"] * (1 + x["innovation_signal_count"]),
        reverse=True,
    )

    total_signals = sum(
        len(i["biomimicry_signals"]) + len(i["tech_signals"]) for i in all_innovations
    )

    return {
        **concept,
        "match_count": len(paper_matches),
        "paper_matches": paper_matches[:10],  # Top 10 papers per concept
        "total_innovation_signals": total_signals,
    }


def build_enhancement_recommendations(cross_ref_results: list[dict]) -> list[dict]:
    """Synthesize cross-reference results into prioritized enhancement recommendations.

    Groups by pillar, deduplicates domains, and ranks by emergent value.
    """
    recommendations = []
    seen_domains: set[str] = set()

    for concept_result in cross_ref_results:
        if concept_result["match_count"] == 0:
            continue

        for paper in concept_result.get("paper_matches", []):
            for signal in paper.get("top_tech_signals", []):
                domain = signal["target_domain"]
                key = f"{concept_result['concept_id']}:{domain}"
                if key in seen_domains:
                    continue
                seen_domains.add(key)

                # Emergent Value = (Capability × Novelty) / (Cost × Risk)
                # Proxy: signal_count * similarity / cost_estimate
                novelty = min(signal["count"] / 5, 1.0)
                capability = paper["max_similarity"]
                cost_estimate = 0.3  # Base integration cost
                ev_score = round((capability * novelty) / cost_estimate, 2)

                recommendations.append(
                    {
                        "concept_id": concept_result["concept_id"],
                        "concept_name": concept_result["name"],
                        "pillar": concept_result["pillar"],
                        "source_paper": paper["paper_name"],
                        "innovation": signal["analogy"],
                        "target_domain": domain,
                        "source_keyword": signal["keyword"],
                        "keyword_count": signal["count"],
                        "similarity": paper["max_similarity"],
                        "emergent_value_score": ev_score,
                        "priority": "high"
                        if ev_score > 2.0
                        else "medium"
                        if ev_score > 1.0
                        else "low",
                        "top_claims": paper.get("top_claims", [])[:2],
                    }
                )

            for signal in paper.get("top_biomimicry_signals", []):
                domain = signal["target_domain"]
                key = f"{concept_result['concept_id']}:bio:{domain}"
                if key in seen_domains:
                    continue
                seen_domains.add(key)

                novelty = min(signal["count"] / 3, 1.0)
                capability = paper["max_similarity"]
                ev_score = round((capability * novelty) / 0.4, 2)

                recommendations.append(
                    {
                        "concept_id": concept_result["concept_id"],
                        "concept_name": concept_result["name"],
                        "pillar": concept_result["pillar"],
                        "source_paper": paper["paper_name"],
                        "innovation": signal["analogy"],
                        "target_domain": domain,
                        "source_keyword": signal["keyword"],
                        "keyword_count": signal["count"],
                        "similarity": paper["max_similarity"],
                        "emergent_value_score": ev_score,
                        "priority": "high"
                        if ev_score > 2.0
                        else "medium"
                        if ev_score > 1.0
                        else "low",
                        "methodology": "biomimicry",
                        "top_claims": paper.get("top_claims", [])[:2],
                    }
                )

    # Sort by emergent value score
    recommendations.sort(key=lambda x: -x["emergent_value_score"])
    return recommendations


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CA-011: Concept-seeded cross-reference engine"
    )
    parser.add_argument(
        "--kg",
        action="store_true",
        help="Query concept IDs and Article nodes from the Knowledge Graph.",
    )
    parser.add_argument(
        "--concept-map",
        type=str,
        default="",
        help="Path to a concept_map.md file to parse concept IDs from.",
    )
    parser.add_argument(
        "--pillars",
        nargs="*",
        default=None,
        help="Filter to specific pillar prefixes (e.g., ORCH KG AHE ECO OS).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.60,
        help="Minimum similarity score for paper-concept matches (default: 0.60).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=15,
        help="Max Article chunks to retrieve per concept query (default: 15).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output file path for JSON results. Prints to stdout if not set.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Process concepts in batches of N (writes intermediate results). 0 = no batching.",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default="",
        help="Resume from a partial output JSON. Skips already-processed concepts.",
    )

    args = parser.parse_args()

    # ── Step 1: Load Concepts ─────────────────────────────────────────
    concepts: list[dict] = []

    if args.concept_map:
        path = Path(args.concept_map)
        if not path.exists():
            print(json.dumps({"error": "Configured concept map was not found"}))
            sys.exit(1)
        concepts = parse_concept_map_file(path)
        print(f"Loaded {len(concepts)} concepts from {path}", file=sys.stderr)

    elif args.kg:
        # Query concept nodes from KG
        try:
            from agent_utilities.knowledge_graph.core.engine import (
                IntelligenceGraphEngine,
            )
            from agent_utilities.core.paths import kg_db_path

            engine = IntelligenceGraphEngine(
                graph=nx.MultiDiGraph(), db_path=str(kg_db_path())
            )
            results = engine.query_cypher(
                "MATCH (n) WHERE n.concept_id IS NOT NULL "
                "RETURN n.concept_id AS concept_id, n.name AS name "
                "ORDER BY n.concept_id"
            )
            if results:
                concepts = parse_concepts_from_kg(results)
            else:
                print(
                    "No concept nodes found in KG. Falling back to concept_map.md search...",
                    file=sys.stderr,
                )
        except Exception as e:
            print(
                f"KG query failed ({type(e).__name__}), falling back to concept_map.md search...",
                file=sys.stderr,
            )

        # Fallback: find concept_map.md in common locations
        if not concepts:
            workspace_root = Path(
                os.environ.get("AGENT_UTILITIES_WORKSPACE_ROOT", Path.cwd())
            ).expanduser()
            package_root = Path(
                os.environ.get(
                    "AGENT_PACKAGES_ROOT", workspace_root / "agent-packages"
                )
            ).expanduser()
            for candidate in [
                Path.cwd() / "docs" / "concept_map.md",
                package_root / "agent-utilities" / "docs" / "concept_map.md",
            ]:
                if candidate.exists():
                    concepts = parse_concept_map_file(candidate)
                    print(
                        f"Loaded {len(concepts)} concepts from a configured source",
                        file=sys.stderr,
                    )
                    break

    if not concepts:
        print(json.dumps({"error": "No concepts found. Use --kg or --concept-map."}))
        sys.exit(1)

    # Filter by pillar if requested
    if args.pillars:
        pillars_upper = {p.upper() for p in args.pillars}
        concepts = [c for c in concepts if c["pillar"] in pillars_upper]

    print(
        f"Cross-referencing {len(concepts)} concepts (threshold={args.threshold}, top_k={args.top_k})...",
        file=sys.stderr,
    )

    # ── Step 2: Load resume state if provided ─────────────────────────
    cross_ref_results: list[dict] = []
    completed_ids: set[str] = set()

    if args.resume:
        resume_path = Path(args.resume)
        if resume_path.exists():
            try:
                resume_data = json.loads(resume_path.read_text())
                cross_ref_results = resume_data.get("cross_reference", [])
                completed_ids = {r["concept_id"] for r in cross_ref_results}
                print(
                    f"Resuming: {len(completed_ids)} concepts already processed.",
                    file=sys.stderr,
                )
            except Exception as e:
                print(f"Failed to load resume file: {type(e).__name__}", file=sys.stderr)

    # Filter out already-completed concepts
    remaining = [c for c in concepts if c["concept_id"] not in completed_ids]
    if not remaining:
        print("All concepts already processed.", file=sys.stderr)
    else:
        print(f"Processing {len(remaining)} remaining concepts...", file=sys.stderr)

    # ── Step 3: Query KG for Article matches per concept ──────────────
    batch_size = args.batch_size if args.batch_size > 0 else len(remaining)

    try:
        from agent_utilities.knowledge_graph.core.engine import IntelligenceGraphEngine
        from agent_utilities.core.paths import kg_db_path

        engine = IntelligenceGraphEngine(
            graph=nx.MultiDiGraph(), db_path=str(kg_db_path())
        )
        start_time = time.time()

        for i, concept in enumerate(remaining):
            query = f"{concept['name']} {concept['pillar_name']}"
            print(
                f"  [{i + 1}/{len(remaining)}] Searching: {concept['concept_id']} — {concept['name']}",
                file=sys.stderr,
            )

            try:
                results = engine.search_hybrid(query, top_k=args.top_k)
                # Filter to Article nodes only
                article_results = [
                    r
                    for r in results
                    if r.get("type", "").lower() in ("article", "document", "")
                ]
                result = cross_reference_concept(
                    concept, article_results, args.threshold
                )
            except Exception as e:
                print(
                    f"    ⚠ Search failed for {concept['concept_id']}: {type(e).__name__}",
                    file=sys.stderr,
                )
                result = {
                    **concept,
                    "match_count": 0,
                    "paper_matches": [],
                    "error": type(e).__name__,
                }

            cross_ref_results.append(result)

            # Write intermediate results after each batch
            if args.output and batch_size > 0 and (i + 1) % batch_size == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta = (len(remaining) - i - 1) / rate if rate > 0 else 0
                print(
                    f"    ✔ Batch checkpoint ({i + 1}/{len(remaining)}) — "
                    f"{rate:.1f} concepts/sec, ETA: {eta:.0f}s",
                    file=sys.stderr,
                )
                _write_intermediate(args.output, concepts, cross_ref_results)

        elapsed = time.time() - start_time
        print(
            f"Completed {len(remaining)} concepts in {elapsed:.1f}s "
            f"({len(remaining) / elapsed:.1f} concepts/sec)",
            file=sys.stderr,
        )

    except ImportError:
        print(
            "agent_utilities not available — cannot query KG directly.", file=sys.stderr
        )
        print(
            "Run this script in an environment with agent-utilities installed,",
            file=sys.stderr,
        )
        print(
            "or use the MCP tools (kg_search) from an agent session.", file=sys.stderr
        )
        sys.exit(1)

    # ── Step 4: Build Recommendations ─────────────────────────────
    recommendations = build_enhancement_recommendations(cross_ref_results)

    # ── Step 5: Output ────────────────────────────────────────
    _write_final(args.output, concepts, cross_ref_results, recommendations)


def _build_output(
    concepts: list[dict],
    cross_ref_results: list[dict],
    recommendations: list[dict] | None = None,
) -> dict:
    """Build the output dictionary."""
    matched_concepts = [r for r in cross_ref_results if r.get("match_count", 0) > 0]
    pillar_summary: dict[str, dict] = {}
    for r in cross_ref_results:
        p = r["pillar"]
        if p not in pillar_summary:
            pillar_summary[p] = {"concepts": 0, "matched": 0, "total_signals": 0}
        pillar_summary[p]["concepts"] += 1
        if r.get("match_count", 0) > 0:
            pillar_summary[p]["matched"] += 1
            pillar_summary[p]["total_signals"] += r.get("total_innovation_signals", 0)

    recs = recommendations or []
    return {
        "domain": "CA-011",
        "domain_name": "Concept Cross-Reference",
        "summary": {
            "total_concepts": len(concepts),
            "concepts_with_matches": len(matched_concepts),
            "total_recommendations": len(recs),
            "high_priority": len([r for r in recs if r["priority"] == "high"]),
            "medium_priority": len([r for r in recs if r["priority"] == "medium"]),
            "low_priority": len([r for r in recs if r["priority"] == "low"]),
            "pillar_summary": pillar_summary,
        },
        "cross_reference": cross_ref_results,
        "recommendations": recs,
    }


def _write_intermediate(
    output_path: str, concepts: list[dict], cross_ref_results: list[dict]
) -> None:
    """Write intermediate checkpoint (no recommendations yet)."""
    output = _build_output(concepts, cross_ref_results)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))


def _write_final(
    output_path: str,
    concepts: list[dict],
    cross_ref_results: list[dict],
    recommendations: list[dict],
) -> None:
    """Write final output with recommendations."""
    output = _build_output(concepts, cross_ref_results, recommendations)
    result_json = json.dumps(output, indent=2)

    if output_path:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result_json)
        print(f"Results written to {out_path}", file=sys.stderr)
    else:
        print(result_json)


if __name__ == "__main__":
    main()
