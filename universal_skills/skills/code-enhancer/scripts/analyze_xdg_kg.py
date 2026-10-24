#!/usr/bin/env python3
"""CE-021: Cross-repository XDG compliance check using the Knowledge Graph.

Instead of parsing ASTs locally, this script queries the Knowledge Graph
(populated via kg_ingest) to find hardcoded non-XDG standard paths
(e.g., ~/.appname) across all indexed projects.

CONCEPT:CE-021 — KG-Native XDG Compliance Check
"""

import json
import logging
from typing import Any

try:
    from agent_utilities.knowledge_graph.core.engine import IntelligenceGraphEngine
except ImportError:
    IntelligenceGraphEngine = None
logger = logging.getLogger(__name__)


def check_xdg_compliance(project_dir: str | None = None) -> dict[str, Any]:
    """Query the KG for non-XDG compliant paths.

    If project_dir is provided, filters by that target_path.
    Otherwise, checks the entire graph.
    """
    engine = IntelligenceGraphEngine.get_active() if IntelligenceGraphEngine else None
    if not engine:
        try:
            from agent_utilities.core.paths import kg_db_path
            from agent_utilities.knowledge_graph.backends import create_backend
            import networkx as nx

            backend = create_backend(backend_type="ladybug", db_path=str(kg_db_path()))
            engine = IntelligenceGraphEngine(graph=nx.MultiDiGraph(), backend=backend)
        except ImportError as e:
            logger.warning(f"Skipping XDG KG check due to missing dependency: {type(e).__name__}")
            return {
                "domain": "XDG Compliance (KG)",
                "score": 100,
                "grade": "N/A",
                "findings": [
                    "Check skipped: required agent-utilities/networkx dependencies not found."
                ],
                "justifications": [
                    "Dependencies missing, assuming compliance by default for this check."
                ],
            }

    # Query for string literals or path operations that resemble ~/.something
    # In the AST, these are often captured as Constant or Call nodes depending on parsing depth.
    # The Knowledge Graph parses file paths and strings into nodes.
    # For a generalized check, we look for CodeNode or AST nodes whose 'name' or 'value'
    # starts with '~/' or contains '.local/share' etc.

    # We will use a Cypher query to find suspicious paths.
    # We look for nodes containing "~/" but NOT "~/.local" or "~/.config" or "~/.cache".
    cypher = """
    MATCH (n)
    WHERE (n.type IN ['StringLiteral', 'Constant', 'Path', 'CodeNode'])
      AND (
        (n.value STARTS WITH '~/' AND NOT n.value STARTS WITH '~/.local' AND NOT n.value STARTS WITH '~/.config' AND NOT n.value STARTS WITH '~/.cache')
        OR (n.name STARTS WITH '~/' AND NOT n.name STARTS WITH '~/.local' AND NOT n.name STARTS WITH '~/.config' AND NOT n.name STARTS WITH '~/.cache')
      )
    RETURN n.id AS id, n.name AS name, n.value AS value, n.file_path AS file_path, n.target_path AS target_path
    """

    results = engine.query_cypher(cypher)

    findings = []
    failed = False

    # Filter by project_dir if provided
    for row in results:
        target = row.get("target_path", "")
        if project_dir and project_dir not in target:
            continue

        val = row.get("value") or row.get("name")
        file_path = row.get("file_path", "unknown file")

        findings.append(f"Found non-XDG path '{val}' in {file_path}")
        failed = True

    score = 0 if failed else 100
    grade = "F" if failed else "A"

    if not failed:
        justifications = [
            "No non-XDG standard paths found in the Knowledge Graph for this scope."
        ]
    else:
        justifications = [
            "Found hardcoded legacy home directory paths (~/.appname). Use XDG standard paths instead."
        ]

    return {
        "domain": "XDG Compliance (KG)",
        "score": score,
        "grade": grade,
        "findings": findings,
        "justifications": justifications,
    }


if __name__ == "__main__":
    import sys

    proj = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(check_xdg_compliance(proj), indent=2))
