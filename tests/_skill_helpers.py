"""Shared helpers for the knowledge skill tests (US-CONTENT-R012 to R015)."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "universal_skills" / "skills"
PRIVATE = re.compile(r"\.arpa\b|\.lan\b|\.internal\b|/home/|/Users/|/var/tmp|https?://|\bmedulla\b|\barbora\b", re.I)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def read(name: str) -> tuple[dict, str]:
    _, head, body = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(head), body


def in_order(body: str, *needles: str) -> bool:
    spots = [body.index(n) for n in needles]
    return spots == sorted(spots)


def lint_clean(name: str) -> None:
    steps, budgets = _load("check_skill_steps"), _load("check_skill_budgets")
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    assert steps.lint_skill(text, name) == []
    assert budgets.lint_folder(SKILLS / name) == []
