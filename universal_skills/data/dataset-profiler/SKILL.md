---
name: dataset-profiler
domain: data
skill_type: skill
description: >-
  Produce a read-only structural and statistical profile of CSV, TSV, JSON, or
  JSON Lines data without emitting raw field values. Use when onboarding an unknown
  dataset, checking its shape, measuring nulls and cardinality, inferring column
  types, or creating evidence for downstream quality rules. Do not use to modify,
  clean, validate against business rules, or upload the dataset.
license: MIT
tags: [data, profiling, schema, statistics, csv, json]
metadata:
  version: '1.2.1'
  author: Genius
---

# Dataset Profiler

Profile a local dataset without changing it or exposing example values.

```bash
python scripts/profile_dataset.py path/to/data.csv
python scripts/profile_dataset.py data.jsonl --limit 50000 --output profile.json
```

The script supports CSV, TSV, top-level JSON objects or arrays of objects, JSONL,
and NDJSON. It reports a SHA-256 fingerprint, row count, observed columns, nulls,
type distribution, bounded distinct count, numeric range/mean, and string-length range.

## Safety and interpretation

- Keep raw values out of the report; cardinality and ranges can still be sensitive,
  so store profiles according to the source dataset's classification.
- Use `--limit` for very large inputs and record that the result is sampled.
- Treat inferred types as observations, not a business schema.
- Stop on malformed records rather than silently dropping them.
- Use `data-quality-auditor` when explicit rules determine pass or fail.
