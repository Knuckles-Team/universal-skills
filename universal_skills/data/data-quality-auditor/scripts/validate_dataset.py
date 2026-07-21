#!/usr/bin/env python3
"""Validate a local tabular dataset against explicit rules without leaking values."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Mapping


INTEGER_RE = re.compile(r"^[+-]?(?:0|[1-9][0-9]*)$")
NUMBER_RE = re.compile(
    r"^[+-]?(?:(?:[0-9]+\.[0-9]*)|(?:[0-9]*\.[0-9]+)|(?:[0-9]+))(?:[eE][+-]?[0-9]+)?$"
)
SUPPORTED_SUFFIXES = {".csv", ".tsv", ".json", ".jsonl", ".ndjson"}
RULE_KEYS = {
    "required_columns",
    "non_null",
    "unique",
    "types",
    "ranges",
    "allowed_values",
    "row_count",
}
TYPE_NAMES = {"string", "integer", "number", "boolean", "datetime", "object", "array"}
MAX_REPORTED_ROWS = 20


def is_null(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def is_datetime(value: str) -> bool:
    candidate = value.strip()
    if "T" not in candidate and "-" not in candidate:
        return False
    try:
        datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def observed_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        candidate = value.strip()
        lowered = candidate.lower()
        if lowered in {"true", "false"}:
            return "boolean"
        if INTEGER_RE.fullmatch(candidate):
            return "integer"
        if NUMBER_RE.fullmatch(candidate):
            return "number"
        if is_datetime(candidate):
            return "datetime"
        return "string"
    return type(value).__name__.lower()


def numeric_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def records(path: Path) -> Iterator[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(
            f"unsupported extension {suffix!r}; expected one of {sorted(SUPPORTED_SUFFIXES)}"
        )
    if suffix in {".csv", ".tsv"}:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t" if suffix == ".tsv" else ",")
            if reader.fieldnames is None:
                raise ValueError("delimited input has no header row")
            for row in reader:
                yield dict(row)
        return
    if suffix in {".jsonl", ".ndjson"}:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"malformed JSON on line {line_number}: {exc.msg}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"JSON line {line_number} is not an object")
                yield row
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed JSON: {exc.msg}") from exc
    rows = payload if isinstance(payload, list) else [payload]
    for row_number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"JSON row {row_number} is not an object")
        yield row


def string_list(value: Any, key: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of column-name strings")
    return value


def validate_rules(rules: Any) -> dict[str, Any]:
    if not isinstance(rules, dict):
        raise ValueError("rule file must contain a JSON object")
    unknown = sorted(set(rules) - RULE_KEYS)
    if unknown:
        raise ValueError("unknown rule keys: " + ", ".join(unknown))
    for key in ("required_columns", "non_null", "unique"):
        string_list(rules.get(key), key)
    types = rules.get("types", {})
    if not isinstance(types, dict) or any(
        not isinstance(column, str) or expected not in TYPE_NAMES
        for column, expected in types.items()
    ):
        raise ValueError(f"types must map column names to one of {sorted(TYPE_NAMES)}")
    ranges = rules.get("ranges", {})
    if not isinstance(ranges, dict):
        raise ValueError("ranges must be an object")
    for column, bounds in ranges.items():
        if not isinstance(column, str) or not isinstance(bounds, dict):
            raise ValueError("each range must map a column name to an object")
        if set(bounds) - {"min", "max"} or not bounds:
            raise ValueError(f"range for {column} must contain only min and/or max")
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in bounds.values()):
            raise ValueError(f"range bounds for {column} must be numbers")
    allowed = rules.get("allowed_values", {})
    if not isinstance(allowed, dict) or any(
        not isinstance(column, str) or not isinstance(values, list)
        for column, values in allowed.items()
    ):
        raise ValueError("allowed_values must map column names to JSON arrays")
    row_count = rules.get("row_count", {})
    if not isinstance(row_count, dict) or set(row_count) - {"min", "max", "exact"}:
        raise ValueError("row_count must contain only min, max, or exact")
    if "exact" in row_count and ({"min", "max"} & set(row_count)):
        raise ValueError("row_count exact cannot be combined with min or max")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in row_count.values()):
        raise ValueError("row_count bounds must be non-negative integers")
    return rules


class Violations:
    def __init__(self) -> None:
        self._data: dict[tuple[str, str], dict[str, Any]] = {}

    def add(self, rule: str, column: str = "", row: int | None = None) -> None:
        key = (rule, column)
        item = self._data.setdefault(
            key,
            {"rule": rule, "column": column or None, "count": 0, "rows": []},
        )
        item["count"] += 1
        if row is not None and len(item["rows"]) < MAX_REPORTED_ROWS:
            item["rows"].append(row)

    def as_list(self) -> list[dict[str, Any]]:
        return [self._data[key] for key in sorted(self._data)]


def audit(path: Path, rules: dict[str, Any]) -> dict[str, Any]:
    violations = Violations()
    observed_columns: set[str] = set()
    unique_seen: dict[str, set[str]] = defaultdict(set)
    row_count = 0
    non_null = string_list(rules.get("non_null"), "non_null")
    unique = string_list(rules.get("unique"), "unique")
    type_rules = rules.get("types", {})
    range_rules = rules.get("ranges", {})
    allowed_rules = rules.get("allowed_values", {})
    allowed_canonical = {
        column: {canonical(value) for value in values}
        for column, values in allowed_rules.items()
    }

    for row_count, row in enumerate(records(path), 1):
        observed_columns.update(str(column) for column in row)
        for column in non_null:
            if column not in row or is_null(row.get(column)):
                violations.add("non_null", column, row_count)
        for column in unique:
            value = row.get(column)
            if is_null(value):
                continue
            fingerprint = hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()
            if fingerprint in unique_seen[column]:
                violations.add("unique", column, row_count)
            else:
                unique_seen[column].add(fingerprint)
        for column, expected in type_rules.items():
            value = row.get(column)
            if is_null(value):
                continue
            actual = observed_type(value)
            compatible = actual == expected or (expected == "number" and actual == "integer")
            if not compatible:
                violations.add("type", column, row_count)
        for column, bounds in range_rules.items():
            value = row.get(column)
            if is_null(value):
                continue
            number = numeric_value(value)
            if number is None:
                violations.add("range_non_numeric", column, row_count)
            elif ("min" in bounds and number < bounds["min"]) or (
                "max" in bounds and number > bounds["max"]
            ):
                violations.add("range", column, row_count)
        for column, allowed in allowed_canonical.items():
            value = row.get(column)
            if is_null(value):
                continue
            if canonical(value) not in allowed:
                violations.add("allowed_values", column, row_count)

    for column in string_list(rules.get("required_columns"), "required_columns"):
        if column not in observed_columns:
            violations.add("required_column", column)
    count_rule = rules.get("row_count", {})
    if "exact" in count_rule and row_count != count_rule["exact"]:
        violations.add("row_count_exact")
    if "min" in count_rule and row_count < count_rule["min"]:
        violations.add("row_count_min")
    if "max" in count_rule and row_count > count_rule["max"]:
        violations.add("row_count_max")

    violation_list = violations.as_list()
    return {
        "passed": not violation_list,
        "dataset_sha256": file_sha256(path),
        "row_count": row_count,
        "column_count": len(observed_columns),
        "rules_evaluated": sorted(key for key in rules if rules[key] not in ({}, [])),
        "violations": violation_list,
        "redaction": "Dataset values are intentionally omitted; row numbers are one-based.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.dataset.is_file():
        parser.error(f"dataset does not exist: {args.dataset}")
    if not args.rules.is_file():
        parser.error(f"rule file does not exist: {args.rules}")
    try:
        rules = validate_rules(json.loads(args.rules.read_text(encoding="utf-8")))
        report = audit(args.dataset, rules)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"validation failed: {type(exc).__name__}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["passed"] or args.warn_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
