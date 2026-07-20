from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


profiler = load_script(
    "dataset_profiler_script",
    "universal_skills/data/dataset-profiler/scripts/profile_dataset.py",
)
quality = load_script(
    "data_quality_script",
    "universal_skills/data/data-quality-auditor/scripts/validate_dataset.py",
)


def test_profile_is_structural_and_redacted(tmp_path: Path) -> None:
    dataset = tmp_path / "people.csv"
    dataset.write_text(
        "id,email,score\n1,secret@example.com,0.5\n2,,1.0\n", encoding="utf-8"
    )

    report = profiler.profile(dataset, limit=None, unique_cap=100)
    rendered = json.dumps(report)

    assert report["row_count"] == 2
    assert report["columns"]["email"]["null_count"] == 1
    assert report["columns"]["score"]["numeric"]["mean"] == 0.75
    assert "secret@example.com" not in rendered


def test_profile_reports_sampling_and_bounded_cardinality(tmp_path: Path) -> None:
    dataset = tmp_path / "rows.jsonl"
    dataset.write_text("\n".join(json.dumps({"id": value}) for value in range(4)), encoding="utf-8")

    sampled = profiler.profile(dataset, limit=2, unique_cap=100)
    bounded = profiler.profile(dataset, limit=None, unique_cap=2)

    assert sampled["sampled"] is True
    assert sampled["row_count"] == 2
    assert bounded["columns"]["id"]["distinct_count"] is None
    assert bounded["columns"]["id"]["distinct_count_lower_bound"] == 3


def test_quality_audit_returns_redacted_violations(tmp_path: Path) -> None:
    dataset = tmp_path / "records.json"
    dataset.write_text(
        json.dumps(
            [
                {"id": 1, "status": "active", "score": 0.4},
                {"id": 1, "status": "forbidden-secret", "score": 2.0},
                {"id": None, "status": "active", "score": 0.3},
            ]
        ),
        encoding="utf-8",
    )
    rules = quality.validate_rules(
        {
            "required_columns": ["id", "created_at"],
            "non_null": ["id"],
            "unique": ["id"],
            "types": {"id": "integer"},
            "ranges": {"score": {"min": 0, "max": 1}},
            "allowed_values": {"status": ["active", "inactive"]},
            "row_count": {"min": 1},
        }
    )

    report = quality.audit(dataset, rules)
    rendered = json.dumps(report)
    violation_rules = {item["rule"] for item in report["violations"]}

    assert report["passed"] is False
    assert {"required_column", "non_null", "unique", "range", "allowed_values"} <= violation_rules
    assert "forbidden-secret" not in rendered
    assert all(set(item) == {"rule", "column", "count", "rows"} for item in report["violations"])


def test_quality_cli_exit_codes(tmp_path: Path) -> None:
    dataset = tmp_path / "data.csv"
    dataset.write_text("id\n1\n1\n", encoding="utf-8")
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"unique": ["id"]}), encoding="utf-8")

    assert quality.main([str(dataset), "--rules", str(rules)]) == 1
    assert quality.main([str(dataset), "--rules", str(rules), "--warn-only"]) == 0


def test_invalid_quality_rules_fail_closed() -> None:
    try:
        quality.validate_rules({"invented_rule": []})
    except ValueError as exc:
        assert "unknown rule keys" in str(exc)
    else:  # pragma: no cover - protects fail-closed behavior
        raise AssertionError("unknown rules must be rejected")
