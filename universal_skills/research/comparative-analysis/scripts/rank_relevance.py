#!/usr/bin/env python3
"""CA-004: Per-Item Relevance Ranking against a target codebase.

Scores all comparison items (research papers, codebases) against a target
codebase across 5 dimensions and produces a ranked output.

Usage:
    # Filesystem-only mode (no KG required)
    python rank_relevance.py /path/to/target /path/to/paper1.pdf /path/to/codebase2

    # KG-enabled mode (queries all ingested items)
    python rank_relevance.py /path/to/target --kg-enabled

    # Show only top N results
    python rank_relevance.py /path/to/target --kg-enabled --top 10

CONCEPT:KG-2.5 — Per-Item Relevance Ranking
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path


def _extract_codebase_profile(codebase_path: str) -> dict:
    """Build a profile of a codebase for comparison."""
    root = Path(codebase_path)
    if not root.is_dir():
        return {"error": f"Not a directory: {codebase_path}"}

    profile: dict = {
        "name": root.name,
        "path": str(root),
        "modules": [],
        "keywords": set(),
        "patterns": set(),
        "entry_points": [],
        "total_files": 0,
    }

    # Walk Python files to extract structure
    for py_file in root.rglob("*.py"):
        if any(part.startswith(".") for part in py_file.parts):
            continue
        profile["total_files"] += 1
        rel = str(py_file.relative_to(root))
        profile["modules"].append(rel)

        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)

            # Detect entry points
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    name_lower = node.name.lower()
                    # MCP tools
                    for deco in node.decorator_list:
                        if isinstance(deco, ast.Attribute) and deco.attr in ("tool", "command"):
                            profile["entry_points"].append(f"mcp:{node.name}")
                    # FastAPI
                    for deco in node.decorator_list:
                        if isinstance(deco, ast.Attribute) and deco.attr in ("get", "post", "put", "delete"):
                            profile["entry_points"].append(f"api:{node.name}")
                    # CLI
                    if name_lower == "main" or name_lower.startswith("cli_"):
                        profile["entry_points"].append(f"cli:{node.name}")

                # Detect patterns
                if isinstance(node, ast.ClassDef):
                    if any("Mixin" in b.id if isinstance(b, ast.Name) else False for b in node.bases):
                        profile["patterns"].add("mixin")
                    if any("Protocol" in b.id if isinstance(b, ast.Name) else False for b in node.bases):
                        profile["patterns"].add("protocol")

            # Extract keywords from docstrings and comments
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    ds = ast.get_docstring(node)
                    if ds:
                        for word in ds.lower().split():
                            if len(word) > 4:
                                profile["keywords"].add(word)

        except (SyntaxError, UnicodeDecodeError):
            continue

    # Also scan pyproject.toml for metadata keywords
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            for line in content.splitlines():
                if "description" in line.lower():
                    words = line.split("=", 1)[-1].strip().strip('"').lower().split()
                    profile["keywords"].update(w for w in words if len(w) > 3)
        except Exception:
            pass

    profile["keywords"] = list(profile["keywords"])[:200]  # Cap for JSON serialization
    profile["patterns"] = list(profile["patterns"])

    return profile


def _extract_paper_profile(paper_path: str) -> dict:
    """Build a profile from a research paper (markdown or text)."""
    path = Path(paper_path)
    if not path.exists():
        return {"error": f"Not found: {paper_path}"}

    profile: dict = {
        "name": path.stem,
        "path": str(path),
        "type": "paper",
        "keywords": set(),
        "concepts": [],
        "is_research": True,
    }

    try:
        content = path.read_text(encoding="utf-8", errors="replace")[:10000]
        content_lower = content.lower()

        # Extract keywords
        words = re.findall(r'\b[a-z]{4,}\b', content_lower)
        word_freq: dict[str, int] = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        # Top 100 by frequency
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
        profile["keywords"] = [w for w, _ in top_words]

        # Extract concept-like terms
        concept_patterns = [
            r"CONCEPT:\w+[\-\d\.]+",
            r"(?:multi-agent|knowledge graph|embedding|orchestration|protocol)",
            r"(?:transformer|attention|reinforcement learning|neural)",
        ]
        for pattern in concept_patterns:
            matches = re.findall(pattern, content_lower)
            profile["concepts"].extend(matches)

        profile["word_count"] = len(words)
        profile["content_sample"] = content[:500]

    except Exception as e:
        profile["error"] = str(e)

    profile["keywords"] = list(profile["keywords"])
    return profile


def score_item(target_profile: dict, item_profile: dict) -> dict:
    """Score an item against a target codebase across 5 dimensions.

    Returns dict with individual dimension scores and composite.
    """
    scores = {
        "semantic": 0.0,      # 0-30: Keyword/concept overlap
        "concept_overlap": 0.0,  # 0-20: Shared technical concepts
        "arch_compat": 0.0,   # 0-20: Architecture pattern alignment
        "innovation": 0.0,    # 0-20: Novel capabilities
        "feasibility": 0.0,   # 0-10: Implementation feasibility
    }

    target_kw = set(target_profile.get("keywords", []))
    item_kw = set(item_profile.get("keywords", []))

    # ── Semantic Relevance (0-30) ──
    if target_kw and item_kw:
        overlap = len(target_kw & item_kw)
        total = min(len(target_kw), len(item_kw))
        if total > 0:
            jaccard = overlap / total
            scores["semantic"] = round(min(30.0, jaccard * 60.0), 2)

    # ── Concept Overlap (0-20) ──
    high_value_concepts = {
        "agent", "orchestration", "knowledge", "graph", "protocol",
        "embedding", "memory", "reasoning", "planning", "coordination",
        "inference", "context", "tool", "model", "pydantic",
    }
    target_concepts = target_kw & high_value_concepts
    item_concepts = item_kw & high_value_concepts
    if target_concepts:
        overlap = len(target_concepts & item_concepts)
        scores["concept_overlap"] = round(min(20.0, overlap * 4.0), 2)

    # ── Architecture Compatibility (0-20) ──
    target_patterns = set(target_profile.get("patterns", []))
    item_patterns = set(item_profile.get("patterns", []))
    if target_patterns and item_patterns:
        pattern_overlap = len(target_patterns & item_patterns)
        scores["arch_compat"] = round(min(20.0, pattern_overlap * 5.0), 2)

    # Papers get architecture score from content keywords
    if item_profile.get("type") == "paper":
        content = item_profile.get("content_sample", "").lower()
        arch_terms = ["plugin", "mixin", "factory", "protocol", "registry", "dependency injection"]
        arch_hits = sum(1 for t in arch_terms if t in content)
        scores["arch_compat"] = max(scores["arch_compat"], round(min(20.0, arch_hits * 5.0), 2))

    # ── Innovation Potential (0-20) ──
    # Items with keywords NOT in target are innovative
    novel_kw = item_kw - target_kw
    if item_kw:
        novelty_ratio = len(novel_kw) / len(item_kw)
        scores["innovation"] = round(min(20.0, novelty_ratio * 20.0), 2)

    # Papers get boosted innovation for research markers
    if item_profile.get("is_research"):
        content = item_profile.get("content_sample", "").lower()
        research_markers = ["novel", "propose", "introduce", "benchmark", "state-of-the-art", "outperform"]
        marker_hits = sum(1 for m in research_markers if m in content)
        scores["innovation"] = min(20.0, scores["innovation"] + marker_hits * 2.0)

    # ── Feasibility (0-10) ──
    # Codebases with similar patterns are more feasible to integrate
    if item_profile.get("type") != "paper":
        # Check if it's a Python project
        item_files = item_profile.get("modules", [])
        has_python = any(f.endswith(".py") for f in item_files)
        has_pyproject = any("pyproject" in f for f in item_files)
        scores["feasibility"] = 4.0
        if has_python:
            scores["feasibility"] += 3.0
        if has_pyproject:
            scores["feasibility"] += 3.0
    else:
        # Papers are less directly feasible
        content = item_profile.get("content_sample", "").lower()
        feas_markers = ["python", "pip", "api", "library", "open-source", "github", "implementation"]
        feas_hits = sum(1 for m in feas_markers if m in content)
        scores["feasibility"] = round(min(10.0, feas_hits * 2.0), 2)

    scores["composite"] = round(
        scores["semantic"] + scores["concept_overlap"] +
        scores["arch_compat"] + scores["innovation"] + scores["feasibility"],
        2,
    )
    scores["composite"] = min(100.0, scores["composite"])

    return scores


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CA-004: Per-Item Relevance Ranking against a target codebase"
    )
    parser.add_argument("target", help="Path to the target codebase")
    parser.add_argument(
        "items", nargs="*",
        help="Paths to papers/codebases to score (filesystem mode)"
    )
    parser.add_argument(
        "--kg-enabled", action="store_true",
        help="Query KG for all ingested items instead of filesystem paths"
    )
    parser.add_argument(
        "--top", type=int, default=0,
        help="Show only top N results (0 = all)"
    )
    args = parser.parse_args()

    # Build target profile
    target_profile = _extract_codebase_profile(args.target)
    if "error" in target_profile:
        print(json.dumps(target_profile))
        sys.exit(1)

    results = []

    if args.kg_enabled:
        # TODO: Query KG for all ingested items when integrated with engine
        print(json.dumps({
            "error": "KG mode requires running via MCP (kg_analyze action='relevance_sweep'). "
                     "Use filesystem mode with explicit paths instead.",
        }))
        sys.exit(1)
    else:
        for item_path in args.items:
            p = Path(item_path)
            if p.is_dir():
                item_profile = _extract_codebase_profile(item_path)
            else:
                item_profile = _extract_paper_profile(item_path)

            if "error" in item_profile:
                results.append({"path": item_path, "error": item_profile["error"]})
                continue

            scores = score_item(target_profile, item_profile)
            results.append({
                "id": item_profile.get("name", p.stem),
                "type": item_profile.get("type", "codebase"),
                "path": item_path,
                **scores,
            })

    # Sort by composite score
    results.sort(key=lambda x: x.get("composite", 0), reverse=True)

    if args.top > 0:
        results = results[:args.top]

    output = {
        "target": target_profile["name"],
        "target_path": target_profile["path"],
        "items_scored": len(results),
        "rankings": results,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
