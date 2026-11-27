---
name: manual-testing-enhanced
domain: development
skill_type: skill
description: Enhanced manual testing workflows
license: MIT
tags: []
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Manual Testing Enhanced

Specialized skill for exploratory testing, curl verification, and structured execution logging.

## Capability

**run_manual_test** — orchestrate a manual testing cycle with structured
notes, using the agent's own shell/Python execution (`python_executor`,
`curl_explorer`) for verification. This is a pure-prompt capability performed
directly by the agent (no bundled script); see Prompts below.

## Steps

1. Baseline the current state of the feature with `curl -s -i <url>` or the relevant command.
   Verify that the response status and body are saved in the ExecutionNotes artifact as the baseline.
2. Execute each verification step using `curl_explorer` or `python_executor`.
   Verify that every command, its output and its exit status are recorded in ExecutionNotes.
3. Compare each observation with the expected behaviour using `diff <(cat expected.txt) <(cat actual.txt)`.
   Verify that every difference is listed as a discrepancy, or that the diff is empty.
4. Report the discrepancies and bugs found from ExecutionNotes, listing them with `grep -n "DISCREPANCY" ExecutionNotes.md` after tagging each one.
   Verify that each reported bug includes the exact reproduction command.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `curl` returns connection refused | Service under test is not running | Start the service, confirm with `curl -s -o /dev/null -w '%{http_code}' <url>`, then re-baseline |
| Baseline differs between runs | State changed by an earlier step | Reset the test data to a known state and record a new baseline before continuing |
| Observation not reproducible | Step order or input was not recorded | Re-run the steps from the ExecutionNotes in order, and add the missing input to the note |

## Prompts
You are an expert at exploratory testing. When asked to verify a feature:
1. Baseline the current state.
2. Execute the verification steps using the available tools.
3. Record every observation in the ExecutionNotes artifact.
4. Report any discrepancies or bugs found.
