#!/usr/bin/env python3
"""CE-035 — Intent & Opportunity Discovery.

Most code-enhancer domains grade what's *wrong*. This one infers the codebase's **intent** and
surfaces **value-add opportunities** to advance that intent — the question "what could this repo
become?", not just "what's broken?". Three opportunity tiers:

1. **Low-hanging fruit** — capability built but not *exposed*: a public module/function with no CLI
   entrypoint, MCP tool, API route, or test referencing it ("reachable ≠ invoked"); plus the
   explicit backlog already in the code (TODO/FIXME/"coming soon").
2. **Implied-but-missing** — the intent implies a lifecycle the code only partly provides (e.g. a
   noun with `create_`/`get_` but no `update_`/`delete_`/`list_`), or stubs/`NotImplementedError`.
3. **Net-new, intent-aligned** — README/docs claim features not found in code (aspirational gaps),
   and code capabilities absent from the README (undocumented value worth surfacing/exposing).

Filesystem-based and language-aware (no LLM, no network) like the other analyzers. Emits the standard
``{domain, score, grade, findings, justifications, ...}`` contract so ``enhance_repo.py`` aggregates
it. The score reflects *intent realization* — higher when the stated intent is well-exposed and has
few unfinished/unexposed gaps.

Usage:
    python analyze_opportunities.py <repo_path> [--json]
    python analyze_opportunities.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kg_native import body_span, repo_symbols  # noqa: E402 - needs the sys.path insert

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_STUB_RAISE_RE = re.compile(r"^\s*raise\s+NotImplementedError\b")

_SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "build",
    "dist",
    "site",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "target",
}
_BACKLOG_RE = re.compile(
    r"\b(TODO|FIXME|XXX|HACK)\b|coming soon|not yet implemented|future work|placeholder",
    re.IGNORECASE,
)
_CRUD_VERBS = (
    "create",
    "add",
    "get",
    "fetch",
    "read",
    "load",
    "list",
    "update",
    "edit",
    "set",
    "delete",
    "remove",
    "drop",
)
_EXPOSURE_MARKERS = (
    "@mcp.tool",
    "mcp.tool(",
    "create_mcp_server",
    "@app.get",
    "@app.post",
    "@router.get",
    "@router.post",
    "@app.route",
    "add_argument",
    "argparse",
    "click.command",
    "@cli.",
    "FastAPI(",
    "APIRouter(",
)


def _py_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*.py"):
        if not any(part in _SKIP_DIRS for part in p.parts):
            out.append(p)
    return out


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def infer_intent(root: Path) -> dict[str, Any]:
    """Infer stated intent from README, pyproject scripts, and docs/concepts."""
    intent: dict[str, Any] = {
        "purpose": "",
        "claimed_features": [],
        "entrypoints": [],
        "concepts": 0,
    }
    readme = next(
        (
            root / n
            for n in ("README.md", "README.rst", "readme.md")
            if (root / n).exists()
        ),
        None,
    )
    if readme:
        text = _read(readme)
        # purpose = first non-heading, non-badge paragraph
        for para in text.split("\n\n"):
            s = para.strip()
            if (
                s
                and not s.startswith(("#", "![", "[!", "<", "|", "*", "_", ">"))
                and "version" not in s.lower()[:20]
            ):
                intent["purpose"] = " ".join(s.split())[:300]
                break
        # claimed features under a Features/Capabilities heading
        feat = re.search(
            r"##+\s*(Features|Capabilities)(.+?)(\n##\s|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if feat:
            intent["claimed_features"] = re.findall(
                r"^[-*]\s+(.+)$", feat.group(2), re.MULTILINE
            )[:30]
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        pt = _read(pyproject)
        block = re.search(r"\[project\.scripts\](.+?)(\n\[|\Z)", pt, re.DOTALL)
        if block:
            intent["entrypoints"] = re.findall(
                r"^([\w\-.]+)\s*=", block.group(1), re.MULTILINE
            )
    for cand in ("docs/concepts.md", "docs/concepts.yaml", "docs/concept_map.md"):
        if (root / cand).exists():
            intent["concepts"] = len(
                re.findall(r"CONCEPT[:\- ]|`[A-Z]+-\d", _read(root / cand))
            )
            break
    return intent


def find_opportunities(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Static scan for the three opportunity tiers.

    KG-native (CE-045): symbol enumeration (public defs, stub bodies) comes from
    the tiered ``kg_native.repo_symbols`` (graph-os code KG, else the engine
    tree-sitter AST, else a local ``ast`` parse) instead of a per-file ``ast.walk``.
    "Referenced anywhere" is a whole-corpus identifier token scan — the same signal
    an ast.Name/ast.Attribute walk gives (does this identifier occur anywhere?),
    without needing a full parse tree.
    """
    low: list[dict[str, Any]] = []
    implied: list[dict[str, Any]] = []
    files = _py_files(root)
    full_text = ""
    file_text: dict[Path, str] = {}
    exposed_files: set[str] = set()
    backlog = 0

    for f in files:
        text = _read(f)
        full_text += text
        file_text[f] = text
        rel = str(f.relative_to(root))
        backlog += len(_BACKLOG_RE.findall(text))
        if any(m in text for m in _EXPOSURE_MARKERS):
            exposed_files.add(rel)

    # A name's own `def foo(`/`class Foo:` site is itself one token occurrence, so
    # "referenced" means the token appears MORE than once — i.e. somewhere beyond
    # its own definition (mirrors the old ast.Name/ast.Attribute walk, which never
    # counted a FunctionDef/ClassDef's own name as a "use").
    _token_counts = Counter(_TOKEN_RE.findall(full_text))
    referenced: set[str] = {name for name, count in _token_counts.items() if count > 1}

    symbols, _tier = repo_symbols(root)
    public_defs: dict[str, str] = {}  # name -> file
    nouns_verbs: dict[str, set[str]] = defaultdict(set)
    stubs = 0

    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sym in symbols:
        fp = str(sym.get("file_path", ""))
        by_file[fp].append(sym)

    for f in files:
        fp = str(f)
        rel = str(f.relative_to(root))
        is_test = rel.startswith("test") or "/test" in rel or "tests/" in rel
        file_syms = sorted(by_file.get(fp, []), key=lambda s: int(s.get("line") or 0))
        text_lines = file_text.get(f, "").splitlines()

        for i, sym in enumerate(file_syms):
            kind = sym.get("kind_detail", "").lower()
            if kind not in ("function", "method", "class"):
                continue
            name = str(sym.get("name", ""))
            if not name:
                continue
            if not name.startswith("_") and not is_test:
                public_defs.setdefault(name, rel)
                # CRUD verb/noun extraction
                m = re.match(rf"({'|'.join(_CRUD_VERBS)})_(\w+)", name)
                if m:
                    nouns_verbs[m.group(2)].add(m.group(1))

            # Stub detection: a function whose body is a single
            # `raise NotImplementedError` statement (blank/comment/docstring
            # lines aside) — approximated via the symbol's line span instead of an
            # ast.Raise/ast.Call body-shape check.
            if kind in ("function", "method"):
                line, end_line = body_span(text_lines, file_syms, i)
                body_lines = [
                    ln.strip()
                    for ln in text_lines[line : max(end_line, line)]
                    if ln.strip() and not ln.strip().startswith(("#", '"""', "'''"))
                ]
                if len(body_lines) == 1 and _STUB_RAISE_RE.match(body_lines[0]):
                    stubs += 1

    # Tier 1 — low-hanging: public capabilities never referenced anywhere (built, not wired/exposed)
    unexposed = [
        {"name": n, "file": f}
        for n, f in sorted(public_defs.items())
        if n not in referenced and f not in exposed_files
    ]
    for u in unexposed[:15]:
        low.append(
            {
                "tier": "low_hanging",
                "opportunity": f"`{u['name']}` ({u['file']}) is a public capability with no caller, "
                f"CLI, MCP tool, or test — expose/wire it or remove it.",
            }
        )
    if backlog:
        low.append(
            {
                "tier": "low_hanging",
                "opportunity": f"{backlog} explicit TODO/FIXME/'coming soon' markers — a ready backlog.",
            }
        )

    # Tier 2 — implied-but-missing: partial CRUD lifecycles + stubs
    write_verbs = {"update", "edit", "set", "delete", "remove", "drop"}
    for noun, verbs in sorted(nouns_verbs.items()):
        if verbs & {"create", "add"} and not (verbs & write_verbs):
            implied.append(
                {
                    "tier": "implied_missing",
                    "opportunity": f"'{noun}' can be created ({sorted(verbs)}) but not "
                    f"updated/deleted/listed — complete the lifecycle.",
                }
            )
    if stubs:
        implied.append(
            {
                "tier": "implied_missing",
                "opportunity": f"{stubs} NotImplementedError stub(s) — unfinished intent.",
            }
        )

    return {"low_hanging": low, "implied_missing": implied[:15]}


def analyze(root: Path) -> dict[str, Any]:
    intent = infer_intent(root)
    opps = find_opportunities(root)

    # Tier 3 — README features vs code (aspirational gaps / undocumented value)
    aspirational: list[dict[str, Any]] = []
    all_code = " ".join(_read(p) for p in _py_files(root)[:400]).lower()
    for feat in intent.get("claimed_features", [])[:20]:
        key = re.sub(r"[^a-z0-9 ]", "", feat.lower()).split()
        key = [w for w in key if len(w) > 4][:2]
        if key and not all(w in all_code for w in key):
            aspirational.append(
                {
                    "tier": "net_new",
                    "opportunity": f"README claims '{feat[:80]}' — not clearly found in code; "
                    f"implement or correct the doc.",
                }
            )

    findings: list[str] = []
    justifications: list[str] = []
    if intent["purpose"]:
        justifications.append(f"Inferred intent: {intent['purpose'][:160]}")
    findings += [o["opportunity"] for o in opps["low_hanging"]]
    findings += [o["opportunity"] for o in opps["implied_missing"]]
    findings += [o["opportunity"] for o in aspirational[:8]]

    # Score: intent realization. Start at 100, subtract for gaps, reward exposure.
    n_opps = len(opps["low_hanging"]) + len(opps["implied_missing"]) + len(aspirational)
    exposed = (
        bool(intent["entrypoints"]) or "@mcp.tool" in all_code or "fastapi(" in all_code
    )
    score = 100
    score -= min(40, n_opps * 3)
    if not intent["purpose"]:
        score -= 10
        findings.append("No clear stated purpose (README intro) — intent is implicit.")
    if not exposed:
        score -= 15
        findings.append(
            "No CLI/MCP/API entrypoint detected — capabilities may be library-only."
        )
    score = max(0, min(100, score))
    grade = (
        "A"
        if score >= 90
        else "B"
        if score >= 80
        else "C"
        if score >= 70
        else "D"
        if score >= 60
        else "F"
    )

    return {
        "domain": "Intent & Opportunity Discovery",
        "score": score,
        "grade": grade,
        "findings": findings[:30] or ["No notable opportunities or gaps detected."],
        "justifications": justifications,
        "intent": intent,
        "opportunities": {
            "low_hanging": opps["low_hanging"],
            "implied_missing": opps["implied_missing"],
            "net_new": aspirational,
        },
    }


def _self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "README.md").write_text(
            "# Widget Manager\n\nManages widgets end to end.\n\n## Features\n- Quantum teleporter\n"
        )
        (repo / "core.py").write_text(
            "def create_widget(x):\n    return x\n\n"
            "def get_widget(i):\n    return i\n\n"
            "def orphan_helper():\n    '''built but never called or exposed'''\n    return 1\n\n"
            "def todo_stub():\n    raise NotImplementedError  # TODO: finish\n"
        )
        rep = analyze(repo)
        assert rep["domain"] == "Intent & Opportunity Discovery"
        assert rep["intent"]["purpose"].startswith("Manages widgets")
        opp_text = json.dumps(rep["opportunities"])
        assert "orphan_helper" in opp_text, "should flag unexposed capability"
        assert "widget" in opp_text.lower(), (
            "should flag create-without-delete lifecycle"
        )
        assert any("Quantum teleporter" in f for f in rep["findings"]), (
            "should flag aspirational README feature"
        )
        assert isinstance(rep["score"], int)
    print("analyze_opportunities self-test: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Intent & Opportunity Discovery (CE-035).")
    p.add_argument("repo", nargs="?")
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        return _self_test()
    target = Path(args.repo or ".").resolve()
    print(json.dumps(analyze(target), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
