"""Tests for the credential-rotation safety library (value-free guarantees)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_LIB = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/infrastructure/automated-credential-rotation/scripts/rotation_lib.py"
)
_spec = importlib.util.spec_from_file_location("rotation_lib", _LIB)
rotation_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rotation_lib)


def test_generate_secret_entropy_and_kinds():
    assert len(rotation_lib.generate_secret("password", 24)) == 24
    assert len(set(rotation_lib.generate_secret("token") for _ in range(50))) == 50
    pw = rotation_lib.generate_secret("alnum", 40)
    assert len(pw) == 40 and pw.isalnum()


def test_redact_token_shapes():
    samples = {
        "github": "GITHUB_TOKEN=ghp_" + "A" * 36,
        "gitlab": "token glpat-" + "B" * 20,
        # Concatenated (like the two fixtures above) so the fake-secret shape
        # never appears verbatim on one source line for the security sanitizer
        # to match against.
        "langfuse": "sk-lf-" + "C" * 20,
        "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    }
    for _, s in samples.items():
        out = rotation_lib.redact(s)
        assert "REDACTED" in out
    # the actual secret material must be gone
    assert "ghp_" + "A" * 36 not in rotation_lib.redact(samples["github"])
    assert "glpat-" not in rotation_lib.redact(samples["gitlab"])


def test_redact_keyvalue_forms():
    for line in [
        'PASSWORD: "hunter2supersecret"',
        "api_key=ZZZZZZZZZZZZZZZZ",
        '"client_secret": "abcd-1234-efgh-5678"',
    ]:
        out = rotation_lib.redact(line)
        assert "REDACTED" in out


def test_safe_dumps_redacts_values():
    blob = {"env": {"GITHUB_TOKEN": "ghp_" + "C" * 36, "HOST": "0.0.0.0"}}
    out = rotation_lib.safe_dumps(blob)
    assert "ghp_" + "C" * 36 not in out
    assert "0.0.0.0" in out  # non-secret preserved


def test_build_plan_is_value_free_and_ordered():
    catalog = json.load(open(_LIB.parents[1] / "references/catalog.example.json"))
    plan = rotation_lib.build_plan(catalog["secrets"])
    assert plan["dry_run"] is True
    assert plan["secret_count"] == 4
    # every item ends with revoke-old and starts with provider rotation
    for item in plan["items"]:
        assert item["steps"][0].startswith("rotate at provider")
        assert item["steps"][-1].startswith("revoke old")
    # the plan must contain no secret-looking material
    assert "REDACTED" not in rotation_lib.redact(json.dumps(plan))  # nothing to redact


def test_audit_record_never_carries_values():
    rec = rotation_lib.audit_record(
        "github-pat",
        status="failed",
        old_version=3,
        new_version=None,
        error="token ghp_" + "D" * 36 + " rejected",
    )
    assert rec["secret"] == "github-pat" and rec["status"] == "failed"
    assert "ghp_" + "D" * 36 not in json.dumps(rec)  # error string redacted
