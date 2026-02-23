---
name: dev-tools
description: A suite of development tools including JWT parser, SQL prettifier, Regex tester, and JSON minifier/diff.
categories: [Development]
tags: [development, utilities, parsing, tools]
---

# Dev Tools

## Overview

This skill provides a suite of development tools, modeled after IT-Tools.

## Capabilities/Tools
*   `jwt`: Parse and decode JWT tokens.
*   `sql-format`: Format/Prettify SQL queries.
*   `regex`: Test regular expressions against text.
*   `user-agent`: Parse User-Agent strings to identify browser and OS constraints.
*   `json-minify`: Compress JSON.
*   `json-diff`: Unified diff of two JSON strings.

## Usage
Run the script `scripts/main.py` with the desired command.

```bash
# Decode JWT
python scripts/main.py jwt --token "eyJhb..."

# Format SQL
python scripts/main.py sql-format --query "SELECT * FROM users WHERE id=1"

# JWT
python scripts/main.py json-minify --json '{"key": "value"}'
```
