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
  version: '1.6.2'
  author: Knuckles-Team
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

## Steps

1. Confirm the dataset is local and its format is supported.
   Run `ls -l path/to/data.csv` and `head -c 300 path/to/data.csv`. Verify that it is CSV, TSV, JSON, JSONL, or NDJSON.
2. Run the profile with a limit for large inputs.
   Run `python scripts/profile_dataset.py data.jsonl --limit 50000 --output profile.json`. Verify that `profile.json` exists.
3. Check fingerprint and sampling.
   Run `python -c "import json;d=json.load(open('profile.json'));print(list(d))"`. Verify that the SHA-256, row count, and columns are present and that sampling is recorded if `--limit` was used.
4. Store the profile according to the dataset's classification.
   Run `grep -c "@" profile.json`. Verify that no raw values leaked into the report.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Script stops on a malformed record | Input has invalid rows | Report the location, ask the owner to fix the data; do not drop rows silently |
| Memory or runtime too high | Dataset too large | Rerun with `--limit` and note that the profile is sampled |
| Unsupported format error | Nested or unsupported JSON | Convert to JSONL of flat objects or an array of objects, then rerun |

## Safety and interpretation

- Keep raw values out of the report; cardinality and ranges can still be sensitive,
  so store profiles according to the source dataset's classification.
- Use `--limit` for very large inputs and record that the result is sampled.
- Treat inferred types as observations, not a business schema.
- Stop on malformed records rather than silently dropping them.
- Use `data-quality-auditor` when explicit rules determine pass or fail.
