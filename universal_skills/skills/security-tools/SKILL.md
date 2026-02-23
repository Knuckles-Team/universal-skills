---
name: security-tools
description: "Security analysis tools including checking Sentry error logs, conducting threat models, analyzing source code git repositories for security ownership and bus factors, and applying security best practices."
categories: [System & Infrastructure]
tags: [security, appsec, threat-model, ownership, sentry, errors, analysis]
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
