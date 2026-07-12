#!/usr/bin/env python3
"""FR-008: Concept traceability for code-enhancer skill.

Scans for CONCEPT:CE-XXX markers in code docstrings, docs, and pytest
markers. Enhanced to also detect @pytest.mark.concept("xxx") decorators,
identify tests/functions missing concept markers, and cross-reference
against a concept registry from AGENTS.md.

KG-native (CE-045): decorator/pytest-marker + function scanning goes through the
graph-os code KG first (a repo already ingested has this for free), then the
engine tree-sitter AST (``kg_native.parse_file_symbols`` — multi-language,
version-independent), and only falls back to a local stdlib ``ast`` parse when
neither is reachable. See ``kg_native.py`` for the tier hierarchy.

CONCEPT:CE-008 — Concept Traceability
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kg_native import (  # noqa: E402 - needs the sys.path insert above
    SKIP_DIRS as _SKIP_DIRS,
)
from kg_native import (  # noqa: E402
    body_span,
    file_symbols_by_line,
    kg_repo_concepts,
)

CONCEPT_PATTERN = re.compile(r"CONCEPT:([A-Z]+-\d+(?:\.\d+)?)")
MARKER_PATTERN = re.compile(
    r'@pytest\.mark\.concept\(\s*["\']([A-Z]+-\d+(?:\.\d+)?)["\']\s*\)'
)
_DECORATOR_CONCEPT_RE = re.compile(
    r'mark\.concept\(\s*["\']([A-Z]+-\d+(?:\.\d+)?)["\']\s*\)'
)


def _decorator_concept_ids(decorators: str) -> list[str]:
    """Extract concept IDs from a symbol's decorator source (e.g.
    ``@pytest.mark.concept("AU-001")``) — replaces the old ast.Call/ast.Attribute
    walk in ``_extract_concept_from_decorator`` with a regex over the engine/local
    tier's already-extracted decorator text."""
    if not decorators:
        return []
    return _DECORATOR_CONCEPT_RE.findall(decorators)


def _scan_concepts_in_files(
    root: Path, glob_pattern: str, source_type: str
) -> list[dict]:
    """Scan files for CONCEPT markers via regex."""
    concepts: list[dict] = []
    for f in root.rglob(glob_pattern):
        if any(skip in f.parts for skip in _SKIP_DIRS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for match in CONCEPT_PATTERN.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            concepts.append(
                {
                    "concept_id": match.group(1),
                    "file": str(f),
                    "line": line_num,
                    "source_type": source_type,
                }
            )
    return concepts


def _scan_pytest_decorators(root: Path) -> tuple[list[dict], list[dict]]:
    """Scan test files for @pytest.mark.concept decorators + CONCEPT: markers.

    KG-native (CE-045): per test file, symbols come from the graph-os code KG when
    ingested, else the engine tree-sitter AST, else a local stdlib ``ast`` parse
    (``kg_native.file_symbols_by_line``) — replacing the old whole-file ast.walk.

    Returns:
        (concepts_found, tests_missing_markers)
    """
    concepts: list[dict] = []
    missing: list[dict] = []

    test_dirs = [root / "tests", root / "test"]
    test_files: list[Path] = []
    for td in test_dirs:
        if td.is_dir():
            test_files.extend(td.rglob("test_*.py"))
            test_files.extend(td.rglob("*_test.py"))
    test_files.extend(root.glob("test_*.py"))
    test_files = list(set(test_files))

    for tf in test_files:
        if any(skip in tf.parts for skip in _SKIP_DIRS):
            continue
        try:
            source = tf.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        source_lines = source.splitlines()

        symbols = [
            s
            for s in file_symbols_by_line(tf)
            if s.get("kind_detail", "").lower() in ("function", "method")
            and str(s.get("name", "")).startswith("test_")
        ]
        for i, sym in enumerate(symbols):
            name = str(sym.get("name", ""))
            line = int(sym.get("line") or 1)
            start, end = body_span(source_lines, symbols, i)
            body_source = "\n".join(source_lines[start - 1 : end])

            has_concept = False
            for concept_id in _decorator_concept_ids(str(sym.get("decorators", ""))):
                has_concept = True
                concepts.append(
                    {
                        "concept_id": concept_id,
                        "file": str(tf),
                        "line": line,
                        "source_type": "test_decorator",
                        "test_name": name,
                    }
                )

            for match in CONCEPT_PATTERN.finditer(body_source):
                has_concept = True
                concepts.append(
                    {
                        "concept_id": match.group(1),
                        "file": str(tf),
                        "line": line,
                        "source_type": "test_docstring",
                        "test_name": name,
                    }
                )

            if not has_concept:
                missing.append({"test_name": name, "file": str(tf), "line": line})

    return concepts, missing


def _scan_function_docstrings(root: Path) -> list[dict]:
    """Scan Python functions >10 lines for missing CONCEPT markers in docstrings.

    KG-native (CE-045): symbols come from the graph-os code KG (Tier 1) when the
    repo is ingested, else the tiered engine/local parse per file.
    """
    missing: list[dict] = []
    py_files = [
        f
        for f in root.rglob("*.py")
        if not any(skip in f.parts for skip in _SKIP_DIRS)
        and "test_" not in f.name
        and not f.name.endswith("_test.py")
    ]

    for f in py_files:
        try:
            source_lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except (OSError, UnicodeDecodeError):
            continue

        symbols = [
            s
            for s in file_symbols_by_line(f)
            if s.get("kind_detail", "").lower() == "function"
        ]
        for i, sym in enumerate(symbols):
            name = str(sym.get("name", ""))
            line = int(sym.get("line") or 1)
            if name.startswith("_") and not name.startswith("__"):
                continue

            start, end = body_span(source_lines, symbols, i)
            length = end - start + 1
            if length < 10:
                continue

            body_text = "\n".join(source_lines[start - 1 : end])
            if not CONCEPT_PATTERN.search(body_text):
                missing.append(
                    {"function": name, "file": str(f), "line": line, "length": length}
                )

    return missing


# A bare concept-ID token (e.g. "KG-2.79", "CE-038") as used in concepts.yaml.
_BARE_ID_PATTERN = re.compile(r"\b([A-Z]{2,}-\d+(?:\.\d+)?)\b")


def _load_concept_registry(root: Path) -> set[str]:
    """Load known concept IDs from the project's canonical registry.

    Recognises BOTH conventions:
      - ``docs/concepts.yaml`` / ``concepts.yml`` — the agent-utilities standard,
        an auto-generated single-source-of-truth registry of bare concept IDs; and
      - ``AGENTS.md`` ``<!-- CONCEPT:xxx -->`` comments / inline ``CONCEPT:`` refs.

    Treating the canonical YAML as a registry is essential: in a marker→yaml
    discipline a concept lives in code + the generated registry, NOT necessarily
    in a hand-written ``.md`` doc, so the registry is what "documented" means.
    """
    registry: set[str] = set()

    for rel in ("docs/concepts.yaml", "docs/concepts.yml", "concepts.yaml", "concepts.yml"):
        p = root / rel
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for match in _BARE_ID_PATTERN.finditer(content):
                registry.add(match.group(1))

    agents_md = root / "AGENTS.md"
    if agents_md.exists():
        try:
            content = agents_md.read_text(encoding="utf-8", errors="ignore")
            for match in re.finditer(r"<!--\s*CONCEPT:(\S+)\s*-->", content):
                registry.add(match.group(1))
            for match in CONCEPT_PATTERN.finditer(content):
                registry.add(match.group(1))
        except Exception:
            pass

    return registry


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def trace_concepts(root_dir: str = ".") -> dict:
    """Trace concept IDs across code, docs, and tests. Detect drift.

    Enhanced with:
    - KG-native (else engine/local-AST) @pytest.mark.concept() decorator scanning
    - Tests-without-concept-markers detection
    - Functions-without-concept-docstrings detection (>10 lines)
    - Concept registry cross-reference from AGENTS.md
    """
    root = Path(root_dir).resolve()

    # KG-native (CE-045): if this repo is already ingested, its CONCEPT markers are
    # a free Cypher query (MENTIONED_IN edges) instead of a full-tree regex re-scan.
    # Falls back to the regex file scan when the KG has no anchor for this repo.
    kg_concepts = kg_repo_concepts(root)
    if kg_concepts:
        code_concepts = [
            {
                "concept_id": r["concept_id"],
                "file": r.get("file_path") or r.get("path") or "",
                "line": 0,
                "source_type": "code",
            }
            for r in kg_concepts
            if r.get("concept_id")
        ]
    else:
        code_concepts = _scan_concepts_in_files(root, "*.py", "code")
    doc_concepts = _scan_concepts_in_files(root, "*.md", "docs")
    test_concepts = []
    for td in [root / "tests", root / "test"]:
        if td.is_dir():
            test_concepts.extend(_scan_concepts_in_files(td, "*.py", "test"))

    # Enhanced: AST-based decorator scanning
    decorator_concepts, tests_missing_markers = _scan_pytest_decorators(root)

    # Enhanced: Functions missing concept docstrings
    functions_missing = _scan_function_docstrings(root)

    # Enhanced: Load concept registry
    registry = _load_concept_registry(root)

    # Merge decorator concepts into test concepts (dedup by concept_id + file + line)
    seen = {(c["concept_id"], c["file"], c["line"]) for c in test_concepts}
    for dc in decorator_concepts:
        key = (dc["concept_id"], dc["file"], dc["line"])
        if key not in seen:
            test_concepts.append(dc)
            seen.add(key)

    all_concepts = code_concepts + doc_concepts + test_concepts

    # Build concept map
    concept_map: dict[str, dict[str, list[dict]]] = {}
    for c in all_concepts:
        cid = c["concept_id"]
        if cid not in concept_map:
            concept_map[cid] = {
                "code": [],
                "docs": [],
                "test": [],
                "test_decorator": [],
                "test_docstring": [],
            }
        source = c["source_type"]
        if source in concept_map[cid]:
            concept_map[cid][source].append(c)
        elif source in ("test", "test_decorator", "test_docstring"):
            concept_map[cid]["test"].append(c)

    # Detect orphans and drift. The canonical registry (concepts.yaml/AGENTS.md)
    # counts as a traceability source: a concept that lives in code + the
    # generated registry is well-traced even without a hand-written .md or a test
    # marker (that is the intended marker→yaml discipline). Requiring code+docs+
    # tests for every concept is the wrong model for such repos and produced
    # large false-positive orphan/drift counts.
    has_registry_source = bool(registry)
    orphans: list[dict] = []
    drift: list[dict] = []
    well_traced = 0

    for cid, sources in concept_map.items():
        has_code = len(sources["code"]) > 0
        has_docs = len(sources["docs"]) > 0
        has_test = (
            len(sources["test"]) > 0
            or len(sources.get("test_decorator", [])) > 0
            or len(sources.get("test_docstring", [])) > 0
        )
        has_registry = cid in registry

        coverage_count = sum([has_code, has_docs, has_test, has_registry])
        present_in = [k for k, v in {
            "code": has_code, "docs": has_docs, "test": has_test, "registry": has_registry,
        }.items() if v]
        if coverage_count >= 2:
            well_traced += 1
        else:
            orphans.append({"concept_id": cid, "present_in": present_in})
        # Genuine drift: a code marker that is NOT in the canonical registry,
        # i.e. the generated registry is stale and needs a rebuild.
        if has_registry_source and has_code and not has_registry:
            drift.append({"concept_id": cid, "present_in": present_in,
                          "missing_from": ["registry"]})

    # Registry cross-reference: concepts in registry but not in code
    unimplemented = []
    if registry:
        found_concepts = set(concept_map.keys())
        for reg_id in registry:
            if reg_id not in found_concepts:
                unimplemented.append(reg_id)

    # Scoring
    total_concepts = len(concept_map)
    score = 100
    findings: list[str] = []

    if total_concepts == 0:
        score = 30
        findings.append("No CONCEPT markers found — traceability not implemented")
    else:
        trace_ratio = well_traced / total_concepts
        if trace_ratio < 0.3:
            score -= 30
            findings.append(
                f"Low traceability ratio: {trace_ratio:.0%} concepts fully traced"
            )
        elif trace_ratio < 0.6:
            score -= 15
        elif trace_ratio < 0.8:
            score -= 5

        if len(orphans) > 5:
            score -= 15
            findings.append(f"{len(orphans)} orphaned concepts (only in one source)")
        elif len(orphans) > 0:
            score -= len(orphans) * 2

        if len(drift) > 5:
            score -= 10
            findings.append(
                f"{len(drift)} concepts with drift (missing from one source)"
            )
        elif len(drift) > 0:
            score -= len(drift)

    # Tests/functions missing concept markers. Requiring a marker on EVERY test
    # and function is unrealistic for a large repo (it implied thousands of
    # "missing" markers). When a canonical registry is in use the discipline is
    # to mark KEY surfaces, not all — so this is INFORMATIONAL there. Only when
    # no registry exists do we apply a small capped nudge.
    if tests_missing_markers:
        if has_registry_source:
            findings.append(
                f"{len(tests_missing_markers)} test functions without concept "
                "markers (informational — mark key tests, not all)"
            )
        else:
            score -= min(10, len(tests_missing_markers))
            findings.append(
                f"{len(tests_missing_markers)} test functions missing concept markers"
            )

    # Enhanced: penalty for functions missing concept docstrings
    if not has_registry_source and len(functions_missing) > 20:
        score -= 10
        findings.append(
            f"{len(functions_missing)} significant functions (>10 lines) "
            f"missing concept markers in docstrings"
        )
    elif not has_registry_source and len(functions_missing) > 10:
        score -= 5

    # Enhanced: unimplemented registry concepts
    if unimplemented:
        findings.append(
            f"{len(unimplemented)} concepts in AGENTS.md registry not found in code: "
            + ", ".join(unimplemented[:5])
        )

    score = max(0, score)

    metrics = {
        "total_concepts": total_concepts,
        "well_traced": well_traced,
        "orphans": len(orphans),
        "drift": len(drift),
        "code_concepts": len(code_concepts),
        "doc_concepts": len(doc_concepts),
        "test_concepts": len(test_concepts),
        "decorator_concepts": len(decorator_concepts),
        "tests_missing_markers": len(tests_missing_markers),
        "functions_missing_docstrings": len(functions_missing),
        "registry_concepts": len(registry),
        "unimplemented_concepts": len(unimplemented),
    }

    justifications = [
        {
            "criterion": "concept_traceability",
            "points": score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"{total_concepts} unique concepts found. "
                f"{well_traced} fully traced (code+docs+tests), "
                f"{len(orphans)} orphans, {len(drift)} drifted. "
                f"{len(tests_missing_markers)} tests without concept markers. "
                f"{len(functions_missing)} functions without concept docstrings."
            ),
        }
    ]

    return {
        "domain": "Concept Traceability",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "metrics": metrics,
        "concept_map": {
            k: {src: len(v) for src, v in sources.items()}
            for k, v in concept_map.items()
            for sources in [v]
        },
        "orphans": orphans[:10],
        "drift": drift[:10],
        "tests_missing_markers": tests_missing_markers[:20],
        "functions_missing_docstrings": functions_missing[:20],
        "unimplemented_concepts": unimplemented,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(trace_concepts(target), indent=2))
