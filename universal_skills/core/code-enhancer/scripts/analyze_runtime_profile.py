#!/usr/bin/env python3
"""CE-036: Runtime profiling (memory + startup + import cost) for code-enhancer.

Measures what a single *running instance* of a project actually costs: the
resident memory and wall time to import/start it, and which transitive imports
dominate that cost. For Python projects this is fully automated and safe -- it
imports the top-level package in an isolated subprocess (it does NOT run the
app's main loop) and ranks the heaviest imports via ``-X importtime``. This is
the exact signal that distinguishes a lightweight TUI/CLI from one that
accidentally drags a multi-hundred-MB dependency (an ML engine, a browser
runtime) into every process. For non-Python ecosystems it emits a language-aware
tool matrix and a neutral score rather than guessing.

Output contract: ``{domain, score, grade, findings, justifications, metrics}``
JSON on stdout, taking the repo path as ``argv[1]``.

CONCEPT:CE-036 - Runtime Profiling
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Budgets (MB resident at import / ms to import). A frontend/CLI that imports to
# <= GOOD stays in the tens of MB; >= BAD means a heavy dependency is loaded into
# every process and should be made lazy or moved behind a service boundary.
RSS_GOOD_MB = 80.0
RSS_BAD_MB = 400.0
IMPORT_GOOD_MS = 300.0
IMPORT_BAD_MS = 2000.0

# Imports that, when pulled into a process unconditionally, usually explain a
# memory blow-up. Surfaced as findings when they appear in the import graph.
HEAVY_IMPORTS = (
    "torch",
    "tensorflow",
    "transformers",
    "sentence_transformers",
    "sklearn",
    "scipy",
    "pandas",
    "numpy",
    "cv2",
    "playwright",
    "selenium",
    "chromadb",
)

LANG_TOOL_MATRIX = {
    "rust": "cargo flamegraph, heaptrack, valgrind --tool=massif, hyperfine",
    "go": "go test -bench / pprof (runtime/pprof), hyperfine",
    "java": "async-profiler, jmap -histo, JFR, hyperfine",
    "node": "node --prof, clinic.js, 0x, hyperfine",
    "typescript": "node --prof, clinic.js, hyperfine",
}


def _score_to_grade(score: float) -> str:
    return (
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


def _detect_language(repo: Path) -> str:
    if (repo / "pyproject.toml").exists() or list(repo.glob("*/__init__.py")):
        return "python"
    if (repo / "Cargo.toml").exists():
        return "rust"
    if (repo / "go.mod").exists():
        return "go"
    if (repo / "pom.xml").exists() or (repo / "build.gradle").exists():
        return "java"
    if (repo / "tsconfig.json").exists():
        return "typescript"
    if (repo / "package.json").exists():
        return "node"
    return "unknown"


def _python_packages(repo: Path) -> list[str]:
    """Best-effort discovery of importable top-level packages in the repo."""
    pkgs: list[str] = []
    # src/ layout and flat layout: dirs with __init__.py that aren't tests/build.
    skip = {"tests", "test", "build", "dist", "docs", "examples", ".venv"}
    for init in repo.glob("*/__init__.py"):
        name = init.parent.name
        if name not in skip and not name.startswith("."):
            pkgs.append(name)
    for init in repo.glob("src/*/__init__.py"):
        pkgs.append(init.parent.name)
    return sorted(set(pkgs))


def _entry_module(repo: Path, packages: list[str]) -> str | None:
    """Resolve the module a console-script imports (where real cost lives).

    The bare top-level ``__init__`` is often near-empty; the import weight of a
    real instance is paid when the entry module loads. Prefer the first
    ``[project.scripts]`` target (``pkg.mod:func`` -> ``pkg.mod``).
    """
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        import tomllib

        data = tomllib.loads(pyproject.read_text())
    except (ImportError, ValueError, OSError):
        return None
    scripts = data.get("project", {}).get("scripts", {})
    for target in scripts.values():
        module = str(target).split(":", 1)[0].strip()
        if module and module.split(".", 1)[0] in packages:
            return module
    return None


def _measure_import_rss(repo: Path, package: str) -> dict[str, Any]:
    """Import ``package`` in a child process; return VmRSS before/after (MB)."""
    probe = (
        "import sys\n"
        "def vmrss():\n"
        "    import re\n"
        "    try:\n"
        "        for l in open('/proc/self/status'):\n"
        "            if l.startswith('VmRSS:'): return int(l.split()[1])/1024.0\n"
        "    except OSError:\n"
        "        import resource\n"
        "        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0\n"
        "    return -1.0\n"
        "before = vmrss()\n"
        f"import {package}\n"
        "after = vmrss()\n"
        "import json\n"
        "print(json.dumps({'before': before, 'after': after}))\n"
    )
    try:
        out = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            cwd=str(repo),
            timeout=120,
        )
        if out.returncode != 0:
            return {"error": (out.stderr or "import failed")[-200:]}
        data = json.loads(out.stdout.strip().splitlines()[-1])
        data["import_rss_mb"] = round(data["after"] - data["before"], 1)
        data["resident_mb"] = round(data["after"], 1)
        return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, IndexError) as e:
        return {"error": type(e).__name__}


def _measure_importtime(repo: Path, package: str) -> dict[str, Any]:
    """Rank the heaviest transitive imports via ``python -X importtime``."""
    try:
        out = subprocess.run(
            [sys.executable, "-X", "importtime", "-c", f"import {package}"],
            capture_output=True,
            text=True,
            cwd=str(repo),
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"error": "importtime timed out"}
    rows: list[tuple[int, str]] = []
    for line in (out.stderr or "").splitlines():
        # format: "import time:  self [us] | cumulative [us] | imported package"
        m = re.match(r"import time:\s*\d+\s*\|\s*(\d+)\s*\|\s*(\S+)", line)
        if m:
            rows.append((int(m.group(1)), m.group(2).strip()))
    rows.sort(reverse=True)
    total_ms = round(rows[0][0] / 1000.0, 1) if rows else 0.0
    heaviest = [
        {"module": name, "cumulative_ms": round(us / 1000.0, 1)}
        for us, name in rows[:10]
    ]
    heavy_present = sorted(
        {
            h
            for h in HEAVY_IMPORTS
            for _us, name in rows
            if name == h or name.startswith(h + ".")
        }
    )
    return {
        "total_import_ms": total_ms,
        "heaviest": heaviest,
        "heavy_dependencies_loaded": heavy_present,
    }


def analyze_runtime_profile(repo_path: str) -> dict[str, Any]:
    repo = Path(repo_path).resolve()
    language = _detect_language(repo)
    findings: list[str] = []
    metrics: dict[str, Any] = {"language": language}

    if language != "python":
        tools = LANG_TOOL_MATRIX.get(language, "hyperfine, /usr/bin/time -v")
        return {
            "domain": "Runtime Profiling",
            "score": 75,
            "grade": "C",
            "findings": [
                f"Automated runtime profiling targets Python; {language} detected.",
                f"Recommended tools for {language}: {tools}.",
            ],
            "justifications": [
                {
                    "criterion": "runtime_profiling",
                    "points": 75,
                    "evidence": f"language={language}",
                    "reasoning": "Neutral score: language-aware tool guidance emitted; "
                    "no automated measurement for this ecosystem.",
                }
            ],
            "metrics": metrics,
        }

    packages = _python_packages(repo)
    if not packages:
        return {
            "domain": "Runtime Profiling",
            "score": 70,
            "grade": "C",
            "findings": ["No importable top-level Python package found to profile."],
            "justifications": [
                {
                    "criterion": "runtime_profiling",
                    "points": 70,
                    "evidence": "no package",
                    "reasoning": "Could not locate an importable package; nothing measured.",
                }
            ],
            "metrics": metrics,
        }

    package = packages[0]
    # Profile the console-script entry module when one exists -- that is where a
    # real instance's import weight is actually paid -- else the bare package.
    target = _entry_module(repo, packages) or package
    metrics["package"] = package
    metrics["profiled_module"] = target
    metrics["packages_found"] = packages

    rss = _measure_import_rss(repo, target)
    importtime = _measure_importtime(repo, target)
    metrics["import"] = rss
    metrics["importtime"] = importtime

    if "error" in rss:
        findings.append(f"Could not import {target}: {rss['error']}")
        score = 60
    else:
        import_rss = rss.get("import_rss_mb", 0.0)
        import_ms = importtime.get("total_import_ms", 0.0)
        findings.append(
            f"Importing `{target}` costs ~{import_rss} MB RSS and ~{import_ms} ms."
        )
        # Budget-based scoring: 60% memory, 40% startup.
        mem_pts = _budget_points(import_rss, RSS_GOOD_MB, RSS_BAD_MB)
        start_pts = _budget_points(import_ms, IMPORT_GOOD_MS, IMPORT_BAD_MS)
        score = round(0.6 * mem_pts + 0.4 * start_pts)
        heavy = importtime.get("heavy_dependencies_loaded", [])
        if heavy:
            findings.append(
                "Heavy dependencies loaded unconditionally at import: "
                + ", ".join(heavy)
                + " - consider lazy-importing them so they don't inflate every process."
            )
        top = importtime.get("heaviest", [])[:3]
        if top:
            findings.append(
                "Slowest imports: "
                + ", ".join(f"{t['module']} ({t['cumulative_ms']}ms)" for t in top)
            )

    grade = _score_to_grade(score)
    return {
        "domain": "Runtime Profiling",
        "score": score,
        "grade": grade,
        "findings": findings,
        "justifications": [
            {
                "criterion": "runtime_profiling",
                "points": score,
                "evidence": json.dumps(
                    {"import_rss_mb": rss.get("import_rss_mb"), **importtime}
                )[:400],
                "reasoning": "Budget-scored on import RSS (good<=%dMB, bad>=%dMB) and "
                "import wall time (good<=%dms, bad>=%dms)."
                % (RSS_GOOD_MB, RSS_BAD_MB, IMPORT_GOOD_MS, IMPORT_BAD_MS),
            }
        ],
        "metrics": metrics,
    }


def _budget_points(value: float, good: float, bad: float) -> float:
    """100 at/below ``good``, 0 at/above ``bad``, linear between."""
    if value <= good:
        return 100.0
    if value >= bad:
        return 0.0
    return round(100.0 * (bad - value) / (bad - good), 1)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_runtime_profile(target), indent=2))
