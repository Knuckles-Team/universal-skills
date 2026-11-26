---
name: data-dictionary-builder
domain: data
skill_type: skill
description: >-
  Convert a dataset profile, declared schema, and domain-owner notes into a concise
  data dictionary with field meanings, types, units, null semantics, sensitivity,
  provenance, and caveats. Use when a dataset needs human-readable documentation
  for analysts, engineers, governance, or handoff. Do not use to infer business
  meaning from column names alone or to alter the dataset.
license: MIT
tags: [data, documentation, schema, governance, lineage]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Data Dictionary Builder

Document the supplied schema and owner-confirmed meaning. Separate observed facts
from interpretations that still require confirmation.

## Inputs

- Dataset identifier, version or fingerprint, owner, source, and refresh cadence.
- Structural profile or schema with types and nullability.
- Domain notes defining business meaning, calculations, units, codes, and known limitations.
- Data-classification and retention requirements when available.

## Steps

1. Collect the schema, profile, and owner notes.
   Run `ls` on the supplied files. Verify that dataset ID, version or fingerprint, owner, and source are recorded.
2. Extract physical fields from the profile.
   Run `python -c "import json;print(list(json.load(open('profile.json'))['columns']))"` or read the schema file. Verify that the list is complete.
3. Write field entries from the Output contract using only owner-confirmed meaning.
   Verify that `grep -c "^| " dictionary.md` covers every field and that inferred items are labeled.
4. Add dataset-level grain, keys, time semantics, lineage, retention, and unresolved questions.
   Run `grep -n -i "unresolved" dictionary.md`. Verify that each unresolved question names an owner.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Column name does not reveal meaning | No domain note exists | Label it unconfirmed and route a question to the named owner |
| Profile and schema disagree | Schema drifted from data | Record both and list the discrepancy as an open question |
| Sensitivity class missing | Classification not supplied | Mark unknown and ask governance for the class |

## Output contract

For each field, record name, business definition, physical type, logical type, unit
or format, nullable meaning, allowed values or reference table, derivation, source,
key or relationship role, sensitivity class, quality expectations, and caveats.

Also include dataset-level grain, primary or candidate keys, time semantics, update
cadence, lineage, joins, access constraints, retention, and unresolved questions.
Never turn a guessed meaning into a definition. Label inferred observations and route
them to the named owner for confirmation.
