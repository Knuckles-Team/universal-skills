#!/usr/bin/env python3
"""CA-010: Innovation extraction — analogical reasoning, biomimicry, emergent value.

Extracts transferable concepts from research papers and identifies hidden
synergies between codebases using Structure Mapping Theory, TRIZ, and
Emergent Value Discovery.

Usage:
    python extract_innovations.py --source /path/to/paper.md --target /path/to/codebase
    python extract_innovations.py --sources /path/to/paper1.md /path/to/paper2.md

    # Concept-ID-aware mode:
    python extract_innovations.py --source /path/to/paper.md --concept-id KG-2.4

    # KG-backed source (pulls Article content from Knowledge Graph):
    python extract_innovations.py --kg-source "hypergraph inductive reasoning" --target /path/to/codebase

CONCEPT:CA-010 — Innovation Extraction Engine
"""

import json
import re
import sys
from pathlib import Path

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
    # ── AI/ML Core ────────────────────────────────────────────────────
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
        "analogy": "macro-action composition for shorter interaction chains",
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
    # ── Knowledge Graph & Ontology ────────────────────────────────────
    "knowledge graph": {"analogy": "structured relational memory", "domain": "kg"},
    "ontology": {
        "analogy": "formal domain modeling with class hierarchies",
        "domain": "owl_reasoning",
    },
    "owl": {
        "analogy": "web ontology language for semantic reasoning",
        "domain": "owl_bridge",
    },
    "rdf": {
        "analogy": "resource description framework triple encoding",
        "domain": "triple_store",
    },
    "sparql": {"analogy": "structured graph query language", "domain": "kg_query"},
    "triple store": {
        "analogy": "subject-predicate-object persistence",
        "domain": "kg_storage",
    },
    "named graph": {
        "analogy": "provenance-scoped subgraph partitioning",
        "domain": "kg_partitioning",
    },
    "semantic web": {
        "analogy": "linked-data interoperability layer",
        "domain": "ontology_bridge",
    },
    "rdfs": {
        "analogy": "schema-level class and property hierarchies",
        "domain": "owl_reasoning",
    },
    "skos": {"analogy": "concept scheme taxonomies", "domain": "schema_packs"},
    # ── Labeled Property Graph (LPG) ──────────────────────────────────
    "property graph": {
        "analogy": "labeled node-edge-property data model",
        "domain": "lpg",
    },
    "labeled property": {
        "analogy": "typed nodes and edges with attribute maps",
        "domain": "lpg",
    },
    "cypher": {
        "analogy": "declarative graph pattern matching",
        "domain": "cypher_query",
    },
    "gremlin": {
        "analogy": "traversal-based graph query language",
        "domain": "graph_traversal",
    },
    "neo4j": {"analogy": "native graph database engine", "domain": "lpg"},
    "graph database": {
        "analogy": "index-free adjacency storage",
        "domain": "graph_storage",
    },
    "networkx": {
        "analogy": "in-memory graph analysis library",
        "domain": "graph_analysis",
    },
    # ── Relational & Data Integration ─────────────────────────────────
    "relational database": {
        "analogy": "tabular entity-relationship storage",
        "domain": "relational_store",
    },
    "foreign key": {
        "analogy": "cross-table referential integrity",
        "domain": "relational_edges",
    },
    "join": {
        "analogy": "cross-entity relationship resolution",
        "domain": "entity_linking",
    },
    "data lake": {
        "analogy": "schema-on-read heterogeneous storage",
        "domain": "data_integration",
    },
    "data pipeline": {
        "analogy": "ETL transformation chain",
        "domain": "data_connector",
    },
    "data lineage": {
        "analogy": "provenance tracking across transformations",
        "domain": "provenance",
    },
    "schema migration": {
        "analogy": "additive structural evolution",
        "domain": "schema_packs",
    },
    "entity resolution": {
        "analogy": "cross-source identity deduplication",
        "domain": "entity_linking",
    },
    # ── Vectorized & Topological ──────────────────────────────────────
    "topology": {
        "analogy": "structural graph analysis and shape metrics",
        "domain": "partitioning",
    },
    "topological": {
        "analogy": "connectivity-preserving structural analysis",
        "domain": "topological_partitioning",
    },
    "vector index": {
        "analogy": "approximate nearest-neighbor search structure",
        "domain": "vector_retrieval",
    },
    "vectorized": {
        "analogy": "batch-parallel numerical computation",
        "domain": "vector_ops",
    },
    "vector database": {
        "analogy": "embedding-native similarity search",
        "domain": "vector_retrieval",
    },
    "hypergraph": {"analogy": "n-ary relationship modeling", "domain": "hyperedges"},
    "partitioning": {
        "analogy": "graph decomposition into coherent substructures",
        "domain": "topological_partitioning",
    },
    "community detection": {
        "analogy": "cluster discovery in relational networks",
        "domain": "graph_clustering",
    },
    "centrality": {
        "analogy": "node importance ranking in graph topology",
        "domain": "graph_analysis",
    },
    "graph embedding": {
        "analogy": "structural position encoding for nodes",
        "domain": "encpi",
    },
    "node2vec": {
        "analogy": "random-walk-based graph representation learning",
        "domain": "graph_embedding",
    },
    "spectral": {
        "analogy": "eigenvalue-based graph decomposition",
        "domain": "spectral_analysis",
    },
    # ── Hierarchical Architecture ─────────────────────────────────────
    "hierarchical": {
        "analogy": "multi-level abstraction layering",
        "domain": "hierarchical_planning",
    },
    "composability": {
        "analogy": "modular building-block assembly",
        "domain": "mcp_composition",
    },
    "layered architecture": {
        "analogy": "dependency-ordered abstraction tiers",
        "domain": "clean_architecture",
    },
    "plugin": {
        "analogy": "hot-swappable capability extension",
        "domain": "plugin_registry",
    },
    "middleware": {
        "analogy": "cross-cutting concern interception layer",
        "domain": "middleware",
    },
    "transitive": {
        "analogy": "inferred multi-hop relationship chains",
        "domain": "owl_transitivity",
    },
    "inference": {
        "analogy": "derived knowledge from explicit assertions",
        "domain": "owl_reasoning",
    },
    "subsumption": {
        "analogy": "class hierarchy inclusion reasoning",
        "domain": "owl_reasoning",
    },
}


def extract_from_text(content: str, concept_id: str = "") -> dict:
    """Extract innovation signals from text content."""
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

    # Extract key claims (sentences with innovation signals)
    claims = []
    sentences = re.split(r"[.!?]\s+", content)
    innovation_signals = [
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
    ]
    for sent in sentences:
        if any(sig in sent.lower() for sig in innovation_signals):
            if len(sent.split()) > 5 and len(sent.split()) < 50:
                claims.append(sent.strip())
    claims = claims[:10]  # Top 10 claims

    return {
        "biomimicry_signals": sorted(biomimicry_hits, key=lambda x: -x["count"]),
        "tech_signals": sorted(tech_hits, key=lambda x: -x["count"]),
        "innovation_claims": claims,
        "concept_id": concept_id,
    }


def resolve_kg_sources(query: str, top_k: int = 10) -> list[dict]:
    """Resolve Article content from the Knowledge Graph via semantic search.

    Args:
        query: Natural language search query.
        top_k: Maximum number of results.

    Returns:
        List of dicts with 'content', 'target_path', 'score'.
    """
    try:
        from agent_utilities.knowledge_graph.core.engine import IntelligenceGraphEngine
        from agent_utilities.core.paths import kg_db_path

        engine = IntelligenceGraphEngine(db_path=str(kg_db_path()))
        results = engine.search_hybrid(query, top_k=top_k)
        sources = []
        for r in results:
            content = r.get("content", r.get("description", ""))
            if content:
                sources.append(
                    {
                        "content": content,
                        "target_path": r.get(
                            "target_path", r.get("file_path", "kg_source")
                        ),
                        "score": r.get("score", 0.0),
                        "node_id": r.get("id", r.get("node_id", "")),
                    }
                )
        return sources
    except ImportError:
        print("agent_utilities not available for KG resolution.", file=sys.stderr)
        return []
    except Exception as e:
        print(f"KG resolution failed: {e}", file=sys.stderr)
        return []


def find_synergies(source_signals: dict, target_path: Path | None) -> list[dict]:
    """Find integration synergies between source innovations and target codebase."""
    synergies = []

    if target_path and target_path.is_dir():
        # Scan target codebase for matching domains
        target_content = ""
        for f in target_path.rglob("*.py"):
            rel = f.relative_to(target_path)
            if any(p in str(rel) for p in {".git", "__pycache__", ".venv"}):
                continue
            try:
                target_content += f.read_text(errors="ignore")[:5000] + "\n"
            except Exception:
                pass

        target_lower = target_content.lower()
        all_signals = source_signals.get("biomimicry_signals", []) + source_signals.get(
            "tech_signals", []
        )

        for signal in all_signals:
            domain = signal["target_domain"]
            keyword = signal["keyword"]
            # Check if target already has this domain
            already_present = (
                domain.replace("_", " ") in target_lower or keyword in target_lower
            )
            synergies.append(
                {
                    "innovation": signal["analogy"],
                    "source_keyword": keyword,
                    "target_domain": domain,
                    "already_in_target": already_present,
                    "integration_type": "enhancement"
                    if already_present
                    else "new_capability",
                    "estimated_value": "high"
                    if not already_present and signal["count"] >= 3
                    else "medium"
                    if not already_present
                    else "low",
                }
            )

    return sorted(
        synergies,
        key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["estimated_value"], 3),
    )


def main():
    sources = []
    target = None
    concept_id = ""
    kg_source_query = ""

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--source" and i + 1 < len(sys.argv):
            sources.append(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--sources" and i + 1 < len(sys.argv):
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                sources.append(sys.argv[i])
                i += 1
        elif sys.argv[i] == "--target" and i + 1 < len(sys.argv):
            target = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--concept-id" and i + 1 < len(sys.argv):
            concept_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--kg-source" and i + 1 < len(sys.argv):
            kg_source_query = sys.argv[i + 1]
            i += 2
        else:
            sources.append(sys.argv[i])
            i += 1

    # Resolve KG sources if --kg-source is provided
    kg_articles = []
    if kg_source_query:
        kg_articles = resolve_kg_sources(kg_source_query)
        if not kg_articles:
            print(
                json.dumps({"error": f"No KG articles found for: {kg_source_query}"}),
                file=sys.stderr,
            )

    if not sources and not kg_articles:
        print(
            json.dumps(
                {
                    "error": "Usage: extract_innovations.py [--source <path>]... [--target <codebase>] [--concept-id <ID>] [--kg-source <query>]"
                }
            )
        )
        sys.exit(1)

    results = []

    # Process KG-sourced articles
    for article in kg_articles:
        signals = extract_from_text(article["content"], concept_id=concept_id)
        synergies = find_synergies(signals, Path(target) if target else None)
        results.append(
            {
                "source": article["target_path"],
                "source_type": "knowledge_graph",
                "node_id": article.get("node_id", ""),
                "relevance_score": article.get("score", 0.0),
                "concept_id": concept_id,
                "signals": signals,
                "synergies": synergies[:15],
                "new_capabilities": len(
                    [
                        s
                        for s in synergies
                        if s.get("integration_type") == "new_capability"
                    ]
                ),
                "enhancements": len(
                    [s for s in synergies if s.get("integration_type") == "enhancement"]
                ),
            }
        )

    # Process filesystem sources
    for src in sources:
        path = Path(src).resolve()
        if not path.exists():
            results.append({"source": str(path), "error": "not found"})
            continue

        if path.is_file():
            try:
                content = path.read_text(errors="ignore")
            except Exception as e:
                results.append({"source": str(path), "error": str(e)})
                continue
        elif path.is_dir():
            content = ""
            for f in path.rglob("*"):
                if f.is_file() and f.suffix in {".md", ".txt", ".rst", ".py"}:
                    try:
                        content += f.read_text(errors="ignore")[:10000] + "\n"
                    except Exception:
                        pass

        signals = extract_from_text(content, concept_id=concept_id)
        synergies = find_synergies(signals, Path(target) if target else None)

        results.append(
            {
                "source": str(path),
                "source_type": "filesystem",
                "concept_id": concept_id,
                "signals": signals,
                "synergies": synergies[:15],
                "new_capabilities": len(
                    [
                        s
                        for s in synergies
                        if s.get("integration_type") == "new_capability"
                    ]
                ),
                "enhancements": len(
                    [s for s in synergies if s.get("integration_type") == "enhancement"]
                ),
            }
        )

    print(
        json.dumps(
            {
                "domain": "CA-010",
                "domain_name": "Innovation Extraction",
                "source_count": len(results),
                "target": target,
                "concept_id": concept_id,
                "kg_source_query": kg_source_query if kg_source_query else None,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
