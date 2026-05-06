#!/usr/bin/env python3
"""CA-008: Performance analysis — benchmarks, footprint, deps, async.

Usage: python analyze_performance.py /path/to/project

CONCEPT:CA-008 — Performance & Cost
"""

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build"}


def detect_benchmarks(project_path: Path) -> dict:
    """Detect benchmark suite presence."""
    signals = {
        "benchmark_dir": any((project_path / d).is_dir() for d in ["benchmarks", "bench", "perf"]),
        "pytest_benchmark": False,
        "criterion": False,
        "k6": (project_path / "k6.js").exists() or (project_path / "loadtest.js").exists(),
    }
    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = f.read_text(errors="ignore")
            if "benchmark" in content.lower():
                signals["pytest_benchmark"] = True
                break
        except Exception:
            pass
    return signals


def analyze_dependency_weight(project_path: Path) -> dict:
    """Analyze dependency tree size and weight."""
    dep_count = 0
    heavy_deps = []

    HEAVY_PACKAGES = {
        "tensorflow": 500, "torch": 800, "pandas": 100, "numpy": 50,
        "scipy": 100, "transformers": 300, "langchain": 200,
        "opencv-python": 150, "scikit-learn": 80,
    }

    for cfg in ["pyproject.toml", "requirements.txt", "package.json"]:
        p = project_path / cfg
        if p.exists():
            try:
                content = p.read_text(errors="ignore")
                if cfg == "package.json":
                    data = json.loads(content)
                    dep_count = len(data.get("dependencies", {}))
                else:
                    lines = content.split("\n")
                    for line in lines:
                        name = re.split(r"[<>=~!\[;,]", line)[0].strip().lower()
                        if name and not name.startswith("#") and not name.startswith("["):
                            dep_count += 1
                            if name in HEAVY_PACKAGES:
                                heavy_deps.append({"name": name, "est_size_mb": HEAVY_PACKAGES[name]})
            except Exception:
                pass

    return {
        "dependency_count": dep_count,
        "heavy_dependencies": heavy_deps,
        "estimated_install_mb": sum(d["est_size_mb"] for d in heavy_deps),
    }


def detect_async_patterns(project_path: Path) -> dict:
    """Detect async/concurrency patterns."""
    patterns = {
        "asyncio": False, "threading": False, "multiprocessing": False,
        "concurrent_futures": False, "async_def_count": 0, "sync_def_count": 0,
    }
    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = f.read_text(errors="ignore")
            if "asyncio" in content or "async def" in content:
                patterns["asyncio"] = True
            if "threading" in content:
                patterns["threading"] = True
            if "multiprocessing" in content:
                patterns["multiprocessing"] = True
            if "concurrent.futures" in content:
                patterns["concurrent_futures"] = True
            patterns["async_def_count"] += len(re.findall(r"async\s+def\s+", content))
            patterns["sync_def_count"] += len(re.findall(r"(?<!async\s)def\s+", content))
        except (OSError, UnicodeDecodeError):
            pass

    total = patterns["async_def_count"] + patterns["sync_def_count"]
    patterns["async_ratio"] = round(patterns["async_def_count"] / max(total, 1) * 100, 1)
    return patterns


def check_container_config(project_path: Path) -> dict:
    """Check container/deployment configuration."""
    return {
        "dockerfile": (project_path / "Dockerfile").exists(),
        "compose": any((project_path / f).exists() for f in ["docker-compose.yml", "compose.yml"]),
        "multi_stage": False,
        "health_check": False,
    }


def score_performance(benchmarks: dict, deps: dict, async_p: dict, container: dict) -> dict:
    """Calculate 0-100 performance score."""
    score = 0
    details = []

    # Benchmarks (25 points)
    if benchmarks.get("benchmark_dir") or benchmarks.get("pytest_benchmark"):
        score += 25
        details.append("Benchmark suite present: +25")
    elif benchmarks.get("k6"):
        score += 15
        details.append("Load test present (k6): +15")

    # Dependency weight (25 points)
    dep_count = deps.get("dependency_count", 0)
    if dep_count <= 10:
        score += 25
        details.append(f"Lightweight deps ({dep_count}): +25")
    elif dep_count <= 25:
        score += 20
        details.append(f"Moderate deps ({dep_count}): +20")
    elif dep_count <= 50:
        score += 15
        details.append(f"Heavy deps ({dep_count}): +15")
    else:
        score += 5
        details.append(f"Very heavy deps ({dep_count}): +5")

    # Async patterns (25 points)
    if async_p.get("asyncio"):
        ratio = async_p.get("async_ratio", 0)
        if ratio >= 50:
            score += 25
            details.append(f"Strong async adoption ({ratio}%): +25")
        elif ratio >= 20:
            score += 15
            details.append(f"Partial async ({ratio}%): +15")
        else:
            score += 10
            details.append(f"Some async ({ratio}%): +10")
    else:
        score += 5
        details.append("No async patterns: +5")

    # Container (25 points)
    if container.get("dockerfile"):
        score += 15
        details.append("Dockerfile present: +15")
    if container.get("compose"):
        score += 10
        details.append("Compose config present: +10")

    grade = "A+" if score >= 95 else "A" if score >= 90 else "B+" if score >= 85 else "B" if score >= 80 else "C+" if score >= 75 else "C" if score >= 70 else "D" if score >= 60 else "F"
    return {"score": min(score, 100), "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_performance.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    benchmarks = detect_benchmarks(project_path)
    deps = analyze_dependency_weight(project_path)
    async_p = detect_async_patterns(project_path)
    container = check_container_config(project_path)
    scoring = score_performance(benchmarks, deps, async_p, container)

    print(json.dumps({
        "domain": "CA-008", "domain_name": "Performance",
        "project": str(project_path),
        "benchmarks": benchmarks, "dependency_weight": deps,
        "async_patterns": async_p, "container": container, "scoring": scoring,
    }, indent=2))


if __name__ == "__main__":
    main()
