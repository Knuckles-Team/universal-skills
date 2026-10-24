#!/usr/bin/env python3
"""Produce a redacted structural profile for a local tabular dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Mapping


INTEGER_RE = re.compile(r"^[+-]?(?:0|[1-9][0-9]*)$")
NUMBER_RE = re.compile(
    r"^[+-]?(?:(?:[0-9]+\.[0-9]*)|(?:[0-9]*\.[0-9]+)|(?:[0-9]+))(?:[eE][+-]?[0-9]+)?$"
)
TRUE_VALUES = {"true", "false"}
SUPPORTED_SUFFIXES = {".csv", ".tsv", ".json", ".jsonl", ".ndjson"}


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
        if lowered in TRUE_VALUES:
            return "boolean"
        if INTEGER_RE.fullmatch(candidate):
            return "integer"
        if NUMBER_RE.fullmatch(candidate):
            return "number"
        if is_datetime(candidate):
            return "datetime"
        return "string"
    return type(value).__name__.lower()


def numeric_value(value: Any, kind: str) -> float | None:
    if kind not in {"integer", "number"} or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def canonical_hash(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    except (TypeError, ValueError):
        encoded = repr(type(value)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class ColumnProfile:
    observed: int = 0
    nulls: int = 0
    types: Counter[str] = field(default_factory=Counter)
    distinct_hashes: set[str] = field(default_factory=set)
    distinct_truncated: bool = False
    numeric_count: int = 0
    numeric_sum: float = 0.0
    numeric_min: float | None = None
    numeric_max: float | None = None
    string_min_length: int | None = None
    string_max_length: int | None = None

    def add(self, value: Any, unique_cap: int) -> None:
        self.observed += 1
        if is_null(value):
            self.nulls += 1
            return
        kind = observed_type(value)
        self.types[kind] += 1
        if not self.distinct_truncated:
            self.distinct_hashes.add(canonical_hash(value))
            if len(self.distinct_hashes) > unique_cap:
                self.distinct_truncated = True
                self.distinct_hashes.clear()
        numeric = numeric_value(value, kind)
        if numeric is not None:
            self.numeric_count += 1
            self.numeric_sum += numeric
            self.numeric_min = numeric if self.numeric_min is None else min(self.numeric_min, numeric)
            self.numeric_max = numeric if self.numeric_max is None else max(self.numeric_max, numeric)
        if kind in {"string", "datetime"}:
            length = len(str(value))
            self.string_min_length = (
                length if self.string_min_length is None else min(self.string_min_length, length)
            )
            self.string_max_length = (
                length if self.string_max_length is None else max(self.string_max_length, length)
            )

    def as_dict(self, row_count: int, unique_cap: int) -> dict[str, Any]:
        missing = row_count - self.observed
        result: dict[str, Any] = {
            "observed_count": self.observed,
            "missing_count": missing,
            "null_count": self.nulls,
            "non_null_count": self.observed - self.nulls,
            "types": dict(sorted(self.types.items())),
            "distinct_count": None if self.distinct_truncated else len(self.distinct_hashes),
            "distinct_count_lower_bound": unique_cap + 1 if self.distinct_truncated else None,
        }
        if self.numeric_count:
            result["numeric"] = {
                "count": self.numeric_count,
                "min": self.numeric_min,
                "max": self.numeric_max,
                "mean": self.numeric_sum / self.numeric_count,
            }
        if self.string_min_length is not None:
            result["string_length"] = {
                "min": self.string_min_length,
                "max": self.string_max_length,
            }
        return result


def profile(path: Path, *, limit: int | None, unique_cap: int) -> dict[str, Any]:
    columns: dict[str, ColumnProfile] = {}
    row_count = 0
    sampled = False
    for row in records(path):
        if limit is not None and row_count >= limit:
            sampled = True
            break
        row_count += 1
        for name, value in row.items():
            columns.setdefault(str(name), ColumnProfile()).add(value, unique_cap)
    return {
        "format": path.suffix.lower().lstrip("."),
        "sha256": file_sha256(path),
        "row_count": row_count,
        "sampled": sampled,
        "row_limit": limit,
        "column_count": len(columns),
        "columns": {
            name: columns[name].as_dict(row_count, unique_cap) for name in sorted(columns)
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--unique-cap", type=int, default=10_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if not args.dataset.is_file():
        parser.error(f"dataset does not exist: {args.dataset}")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.unique_cap < 1:
        parser.error("--unique-cap must be at least 1")
    try:
        report = profile(args.dataset, limit=args.limit, unique_cap=args.unique_cap)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"profile failed: {type(exc).__name__}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
