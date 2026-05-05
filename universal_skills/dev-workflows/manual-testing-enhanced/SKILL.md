---
version: '0.5.0'
---

# Manual Testing Enhanced

Specialized skill for exploratory testing, curl verification, and structured execution logging.

## Tools
- `run_manual_test`: Orchestrates a manual testing cycle with structured notes.
- `python_executor`: Runs python code for verification.
- `curl_explorer`: Performs HTTP requests for API verification.

## Prompts
You are an expert at exploratory testing. When asked to verify a feature:
1. Baseline the current state.
2. Execute the verification steps using the available tools.
3. Record every observation in the ExecutionNotes artifact.
4. Report any discrepancies or bugs found.
