#!/usr/bin/env python3
"""CE-037: Scale profiling - how many instances fit in a memory budget.

Answers "how many of these can I run on a Raspberry Pi / small node?" by spawning
N idle instances of the project concurrently, sampling their real resident memory,
and projecting the instances-per-GB density against common RAM sizes. For Python
it spawns child processes that import the entry module and idle (a faithful proxy
for a just-started instance's base footprint) without running the app's main loop.

This domain *executes the target*, so it is opt-in: it only runs when explicitly
requested (``--domains scale_profile``), never in the default sweep.

Output contract: ``{domain, score, grade, findings, justifications, metrics}``
JSON on stdout, taking the repo path as ``argv[1]``. Optional ``argv[2]`` = N
(default 8).

CONCEPT:CE-037 - Scale Profiling
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Density targets: instances that should fit per GB of RAM. A lean CLI/TUI clears
# GOOD; something dragging a heavy runtime into every process falls below BAD.
PER_GB_GOOD = 12.0
PER_GB_BAD = 2.0
COMMON_RAM_GB = (1, 2, 4, 8)


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


def _python_packages(repo: Path) -> list[str]:
    skip = {"tests", "test", "build", "dist", "docs", "examples", ".venv"}
    pkgs = [
        init.parent.name
        for init in repo.glob("*/__init__.py")
        if init.parent.name not in skip and not init.parent.name.startswith(".")
    ]
    pkgs += [init.parent.name for init in repo.glob("src/*/__init__.py")]
    return sorted(set(pkgs))


def _entry_module(repo: Path, packages: list[str]) -> str | None:
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        import tomllib

        data = tomllib.loads(pyproject.read_text())
    except (ImportError, ValueError, OSError):
        return None
    for target in data.get("project", {}).get("scripts", {}).values():
        module = str(target).split(":", 1)[0].strip()
        if module and module.split(".", 1)[0] in packages:
            return module
    return None


def _child_rss_mb(pid: int) -> float:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    except OSError:
        return -1.0
    return -1.0


def _spawn_instances(repo: Path, module: str, n: int) -> dict[str, Any]:
    """Spawn N child processes importing ``module`` and idling; sum their RSS."""
    body = f"import {module}\nimport sys\nsys.stdin.readline()\n"
    procs: list[subprocess.Popen] = []
    try:
        for _ in range(n):
            procs.append(
                subprocess.Popen(
                    [sys.executable, "-c", body],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    cwd=str(repo),
                )
            )
        time.sleep(2.0)  # allow imports to settle
        alive = [p for p in procs if p.poll() is None]
        rss = [_child_rss_mb(p.pid) for p in alive]
        rss = [r for r in rss if r > 0]
        if not rss:
            err = ""
            for p in procs:
                if p.poll() is not None and p.stderr:
                    err = p.stderr.read().decode()[-200:]
                    break
            return {"error": err or "no instances stayed alive"}
        return {
            "spawned": n,
            "alive": len(alive),
            "per_instance_mb": round(sum(rss) / len(rss), 1),
            "aggregate_mb": round(sum(rss), 1),
            "min_mb": round(min(rss), 1),
            "max_mb": round(max(rss), 1),
        }
    finally:
        for p in procs:
            try:
                if p.stdin:
                    p.stdin.write(b"\n")
                    p.stdin.flush()
                p.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                p.kill()


def analyze_scale_profile(repo_path: str, n: int = 8) -> dict[str, Any]:
    repo = Path(repo_path).resolve()
    packages = _python_packages(repo)
    if not packages:
        return {
            "domain": "Scale Profiling",
            "score": 70,
            "grade": "C",
            "findings": ["Scale profiling currently targets Python; no package found."],
            "justifications": [
                {
                    "criterion": "scale_profiling",
                    "points": 70,
                    "evidence": "no package",
                    "reasoning": "Nothing to spawn; neutral score.",
                }
            ],
            "metrics": {"language_supported": False},
        }

    module = _entry_module(repo, packages) or packages[0]
    result = _spawn_instances(repo, module, n)
    metrics: dict[str, Any] = {
        "profiled_module": module,
        "requested_instances": n,
        **result,
    }

    if "error" in result:
        return {
            "domain": "Scale Profiling",
            "score": 60,
            "grade": "D",
            "findings": [f"Could not spawn instances of {module}: {result['error']}"],
            "justifications": [
                {
                    "criterion": "scale_profiling",
                    "points": 60,
                    "evidence": result["error"][:200],
                    "reasoning": "Spawn failed; cannot measure density.",
                }
            ],
            "metrics": metrics,
        }

    per_instance = result["per_instance_mb"]
    per_gb = round(1024.0 / per_instance, 1) if per_instance > 0 else 0.0
    metrics["instances_per_gb"] = per_gb
    metrics["projection"] = {f"{gb}GB": int(per_gb * gb) for gb in COMMON_RAM_GB}

    score = round(
        _budget_points(per_gb, PER_GB_BAD, PER_GB_GOOD, higher_is_better=True)
    )
    findings = [
        f"Idle instance footprint ~{per_instance} MB "
        f"(min {result['min_mb']} / max {result['max_mb']} across {result['alive']}).",
        f"Density ~{per_gb} instances/GB - projected "
        + ", ".join(f"{gb}GB->{int(per_gb * gb)}" for gb in COMMON_RAM_GB)
        + " (idle base RSS; live sessions add per-workload memory).",
    ]
    return {
        "domain": "Scale Profiling",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": [
            {
                "criterion": "scale_profiling",
                "points": score,
                "evidence": json.dumps(
                    {"per_instance_mb": per_instance, "instances_per_gb": per_gb}
                ),
                "reasoning": "Scored on instances/GB density "
                f"(good>={PER_GB_GOOD}, bad<={PER_GB_BAD}).",
            }
        ],
        "metrics": metrics,
    }


def _budget_points(
    value: float, bad: float, good: float, *, higher_is_better: bool
) -> float:
    if higher_is_better:
        if value >= good:
            return 100.0
        if value <= bad:
            return 0.0
        return round(100.0 * (value - bad) / (good - bad), 1)
    if value <= good:
        return 100.0
    if value >= bad:
        return 0.0
    return round(100.0 * (bad - value) / (bad - good), 1)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    print(json.dumps(analyze_scale_profile(target, count), indent=2))
