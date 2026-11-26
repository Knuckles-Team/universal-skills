---
name: security-tools
domain: infrastructure
skill_type: skill
description: >-
  Security analysis tools including checking Sentry error logs, conducting threat
  models, analyzing source code git repositories for security ownership and bus
  factors, and applying security best practices.
license: MIT
tags: [security, appsec, threat-model, ownership, sentry, errors, analysis]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---
# Security Tools

## Overview

This skill consolidates tools and workflows for analyzing the security posture, operational errors, and ownership metrics of an application.

## Steps

1. Pick the analysis from the request (Sentry errors, ownership and bus factor, threat model, or false-positive filtering) with `ls scripts/`. Verify that the request names a project, repository or register to analyse, and ask for it if not.
2. For Sentry, export `SENTRY_AUTH_TOKEN` and run `python scripts/sentry_api.py --project <project> list-issues`. Verify that the output lists issues, or drill in with the `issue-detail` subcommand on one issue id.
3. For ownership, build the map with `python scripts/run_ownership_map.py --repo <repo> --out ownership-map-out`. Verify that `ls ownership-map-out` shows `people.csv`, `files.csv` and `edges.csv`.
4. Query the map with `python scripts/query_ownership.py --data-dir ownership-map-out files --bus-factor-max 1`. Verify that the JSON lists the sensitive files held by a single maintainer.
5. For a security register, run `filter_findings(register)` from `code-enhancer/scripts/findings_filter.py`. Verify that the returned `stats` accounts for each excluded finding.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `sentry_api.py` rejects the base URL | `SENTRY_BASE_URL` is not HTTPS and not loopback | Set an `https://` URL, and add a CA bundle via `SSL_CERT_FILE` if the certificate is private |
| `sentry_api.py` returns an authorisation error | `SENTRY_AUTH_TOKEN` is missing, expired or lacks project scope | Export a fresh token with read scope for the project and retry the same command |
| `query_ownership.py` finds no CSV files | `--data-dir` does not match the `--out` directory of the build | Point `--data-dir` at the build output or rebuild with `run_ownership_map.py` |
| Ownership map is empty or very slow | The repo is a shallow clone, or has a long history | Fetch full history with `git fetch --unshallow`, or limit the build with `--since <date>` |

## Capabilities/Tools
Interact with the Sentry API to inspect application errors and tracebacks.
```bash
# Requires SENTRY_AUTH_TOKEN in the environment
python scripts/sentry_api.py --project my-project list-issues
```

`SENTRY_BASE_URL` must be HTTPS unless it is loopback. The client rejects
redirects and ambient proxies, accepts only the configured host, bounds every
response, and reads optional CA trust from `SSL_CERT_FILE`, `SSL_CERT_DIR`, or
`REQUESTS_CA_BUNDLE` without persisting environment-specific paths.

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

## Related skill

- `security-tools-security-threat-model` — the security-threat-model sub-skill, served as its own skill.
