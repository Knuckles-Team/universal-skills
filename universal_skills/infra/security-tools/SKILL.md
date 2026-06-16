---
name: security-tools
description: >-
  Security analysis tools including checking Sentry error logs, conducting threat
  models, analyzing source code git repositories for security ownership and bus
  factors, and applying security best practices.
license: MIT
tags: [security, appsec, threat-model, ownership, sentry, errors, analysis]
metadata:
  author: Genius
  version: '0.46.0'
---
# Security Tools

## Overview

This skill consolidates tools and workflows for analyzing the security posture, operational errors, and ownership metrics of an application.

## Capabilities/Tools
Interact with the Sentry API to inspect application errors and tracebacks.
```bash
# Requires SENTRY_AUTH_TOKEN in the environment
python scripts/sentry_api.py --project my-project list-issues
```

## 2. Security Ownership Maps (`scripts/`)
Analyze git histories and identify which users own the most sensitive files, or calculate bus factor (how catastrophic losing a single maintainer would be to security knowledge).
- `scripts/build_ownership_map.py`: Parses git logs to output ownership data.
- `scripts/query_ownership.py`: Interrogates the built ownership data.
- `scripts/community_maintainers.py`: Resolves email boundaries for authors.

## 3. Threat Modeling & Best Practices (`docs/`)
Follow established application security frameworks from the `docs/` directory when explicitly requested.
- Review design documents systematically using STRIDE.
- Apply secure-by-default coding conventions to Python, JS/TS, and Go codebases.
- Do NOT perform performative threat modeling unless explicitly requested by the user. Keep assessments focused on actual abuse paths, assets, and boundaries.

## 4. False-Positive Filtering (shared, CE-041)
When triaging a security register (your own findings, or `code-enhancer`'s
`analyze_security.py` output), reduce noise with the shared two-stage filter
`code-enhancer/scripts/findings_filter.py` instead of hand-tuning regexes:

- **Hard-exclusion stage** (deterministic, no network) drops the chronic
  low-signal classes — generic DOS/resource-exhaustion, "add rate limiting"
  advice, resource leaks, open redirects, regex-injection, memory-safety findings
  outside C/C++, and SSRF in static HTML. Findings on each finding's
  `{name, detail, file}` shape.
- **LLM confidence stage** *(opt-in)* — in an agent-driven review (where a model
  is available), pass a `judge(finding) -> (keep, confidence 1–10, reason)`
  callable to `filter_findings(...)`; findings below confidence 8 are dropped,
  and a judge error safely **keeps** the finding. Use this to apply
  organization-specific context ("we use Cognito for auth; don't flag missing
  password validation") — the natural-language equivalent of custom exclusion
  rules.

```python
from findings_filter import filter_findings  # code-enhancer/scripts on path
kept, excluded, stats = filter_findings(register)            # deterministic
kept, excluded, stats = filter_findings(register, judge=my_llm_judge)  # + LLM
```

Borrowed from Anthropic's `claude-code-security-review` (MIT).
