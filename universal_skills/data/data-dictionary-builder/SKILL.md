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
  version: '1.2.1'
  author: Genius
---

# Data Dictionary Builder

Document the supplied schema and owner-confirmed meaning. Separate observed facts
from interpretations that still require confirmation.

## Inputs

- Dataset identifier, version or fingerprint, owner, source, and refresh cadence.
- Structural profile or schema with types and nullability.
- Domain notes defining business meaning, calculations, units, codes, and known limitations.
- Data-classification and retention requirements when available.

## Output contract

For each field, record name, business definition, physical type, logical type, unit
or format, nullable meaning, allowed values or reference table, derivation, source,
key or relationship role, sensitivity class, quality expectations, and caveats.

Also include dataset-level grain, primary or candidate keys, time semantics, update
cadence, lineage, joins, access constraints, retention, and unresolved questions.
Never turn a guessed meaning into a definition. Label inferred observations and route
them to the named owner for confirmation.
