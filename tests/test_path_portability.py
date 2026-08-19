#!/usr/bin/python
"""Cross-platform path-safety helpers (Windows/macOS/Linux)."""

from __future__ import annotations

import hashlib
import os
import sys

import pytest

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
    assert all(len(component) <= 80 for component in rel.split("/"))
    assert "/" in rel and rel.endswith(".md")


def test_portable_relpath_boundary_and_one_under_keep_the_digest_floor():
    original = "leaf" * 80 + ".md"
    digest = hashlib.sha256(original.encode("utf-8")).hexdigest()[:32]

    boundary = portable_relpath([original], max_name=80, max_total=80)
    one_under = portable_relpath([original], max_name=80, max_total=79)

    assert len(boundary) == 80
    assert len(one_under) == 79
    assert boundary.endswith(".md") and one_under.endswith(".md")
    assert digest in boundary and digest in one_under


def test_portable_relpath_unicode_and_case_folded_inputs_remain_distinct():
    upper = "Ä" * 100 + ".md"
    lower = "ä" * 100 + ".md"

    upper_path = portable_relpath([upper], max_name=80, max_total=79)
    lower_path = portable_relpath([lower], max_name=80, max_total=79)

    assert len(upper_path) <= 79 and len(lower_path) <= 79
    assert upper_path != lower_path
    assert upper_path.casefold() != lower_path.casefold()


def test_portable_relpath_reserved_component_and_component_budget():
    rel = portable_relpath(["CON", "x" * 160 + ".md"], max_name=80, max_total=120)

    components = rel.split("/")
    assert components[0] == "CON_"
    assert all(len(component) <= 80 for component in components)
    assert len(rel) <= 120


def test_portable_relpath_refuses_budget_below_digest_floor():
    with pytest.raises(ValueError, match="budget"):
        portable_relpath([], max_total=0)

    with pytest.raises(ValueError, match="safe digest"):
        portable_relpath(["x" * 100], max_name=80, max_total=33)

    with pytest.raises(ValueError, match="safe digest"):
        portable_relpath(
            ["a" * 100, "b" * 100, "c" * 100],
            max_name=80,
            max_total=100,
        )


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
