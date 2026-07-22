---
name: manual-testing-enhanced
domain: development
skill_type: skill
description: Enhanced manual testing workflows
license: MIT
tags: []
metadata:
  version: '1.2.1'
  author: Genius
---

# Manual Testing Enhanced

Specialized skill for exploratory testing, curl verification, and structured execution logging.

## Capability

**run_manual_test** — orchestrate a manual testing cycle with structured
notes, using the agent's own shell/Python execution (`python_executor`,
`curl_explorer`) for verification. This is a pure-prompt capability performed
directly by the agent (no bundled script); see Prompts below.

## Prompts
You are an expert at exploratory testing. When asked to verify a feature:
1. Baseline the current state.
2. Execute the verification steps using the available tools.
3. Record every observation in the ExecutionNotes artifact.
4. Report any discrepancies or bugs found.
