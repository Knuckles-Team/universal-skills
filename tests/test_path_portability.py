#!/usr/bin/python
"""Cross-platform path-safety helpers (Windows/macOS/Linux)."""

from __future__ import annotations

import os
import sys

from universal_skills.skill_utilities import (
    dedupe_caseless,
    portable_name,
    portable_relpath,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from check_path_portability import scan  # noqa: E402


def test_portable_name_strips_illegal_and_reserved():
    assert portable_name('a<b>c:"d|e?f*g') == "a-b-c--d-e-f-g"
    assert portable_name("CON").upper().startswith("CON_")
    assert portable_name("name.") == "name"  # trailing dot dropped
    assert portable_name("  spaced  ").strip() == portable_name("  spaced  ")


def test_portable_name_truncates_with_hash_and_keeps_ext():
    long = "x" * 300 + ".md"
    out = portable_name(long, max_len=80)
    assert len(out) <= 80
    assert out.endswith(".md")
    # distinct long inputs stay distinct (hash suffix)
    assert portable_name("a" * 300 + ".md") != portable_name("b" * 300 + ".md")


def test_portable_relpath_bounds_total_length():
    parts = ["dir" * 30, "sub" * 30, "leaf" * 40 + ".md"]
    rel = portable_relpath(parts, max_total=180)
    assert len(rel) <= 180
    assert "/" in rel and rel.endswith(".md")


def test_dedupe_caseless_resolves_collisions():
    out = dedupe_caseless(["Queues.md", "queues.md", "Other.md"])
    assert out["Queues.md"] == "Queues.md"
    assert out["queues.md"] == "queues-2.md"
    assert out["Other.md"] == "Other.md"


def test_checker_flags_violations(tmp_path):
    (tmp_path / "ok.md").write_text("x")
    (tmp_path / "Dup.md").write_text("x")
    (tmp_path / "dup.md").write_text("x")  # case collision
    (tmp_path / ("y" * 150 + ".md")).write_text("x")  # long name
    rep = scan(str(tmp_path), max_path=200, max_name=100)
    assert rep["case_collision"]
    assert rep["long_name"]
