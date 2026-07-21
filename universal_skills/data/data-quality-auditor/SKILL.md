---
name: data-quality-auditor
domain: data
skill_type: skill
description: >-
  Validate CSV, TSV, JSON, or JSON Lines data against an explicit JSON rule set and
  emit a redacted, machine-readable pass/fail report. Use when checking required
  columns, nullability, uniqueness, types, ranges, allowed values, or row-count
  expectations before analysis or ingestion. Do not use to repair data or infer
  unstated business rules.
license: MIT
tags: [data, quality, validation, schema, rules, csv, json]
metadata:
  version: '1.2.1'
  author: Genius
---

# Data Quality Auditor

Run deterministic checks from a reviewed rule file:

```bash
python scripts/validate_dataset.py data.csv --rules quality-rules.json
```

Supported rule keys are `required_columns`, `non_null`, `unique`, `types`,
`ranges`, `allowed_values`, and `row_count`. The report contains counts and row
numbers but never raw failing values. The command exits nonzero on violations;
use `--warn-only` only when a non-blocking audit is explicitly intended.

## Rule example

```json
{
  "required_columns": ["id", "created_at"],
  "non_null": ["id"],
  "unique": ["id"],
  "types": {"id": "integer", "created_at": "datetime"},
  "ranges": {"score": {"min": 0, "max": 1}},
  "allowed_values": {"status": ["active", "inactive"]},
  "row_count": {"min": 1}
}
```

Review the rules and dataset authorization before running. A passing report proves
only the declared checks; it does not establish correctness, fairness, fitness for
purpose, or permission to use the data.
