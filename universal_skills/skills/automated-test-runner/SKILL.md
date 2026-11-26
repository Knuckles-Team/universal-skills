---
name: automated-test-runner
skill_type: skill
description: >
  Universal automated testing atomic skill. Discovers environment, executes
  test suite with timeouts, and compiles execution outcomes.
domain: development
license: MIT
tags: [testing, verification, quality, CI, automation]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
requires:
  - rep_rm_projects
---

# Automated Test Runner Skill

Stateless atomic operation to discover the build environment of a target project, execute its automated unit/integration test suites with strict timeouts, and compile the test outcomes into a standardized, rich JSON schema.

## Prerequisites

- `rep_rm_projects` — for bulk workspace operations, dependency tracking, and cross-project package orchestration.

## Steps

1. Detect the project ecosystem by running `ls` on the project root for `pyproject.toml`, `package.json`, `Cargo.toml` or `go.mod`. Verify that exactly one runner (`pytest`, `npm test`, `cargo test` or `go test ./...`) is selected from the manifest found.
2. Execute the suite by running the selected command under a 300 second timeout, such as `timeout 300 pytest --verbose`. Verify that the exit code and the captured stdout and stderr are recorded.
3. Compile the results by parsing the captured output into the JSON object with `status`, `metrics` and `failures`. Verify that `metrics.total` equals passed plus failed plus skipped.


### Step 1: discover_build_environment
Analyze the project workspace directory to detect the engineering ecosystem and select the matching testing runner:
- Inspect files in the target project root folder to identify standard build manifests:
  - Python: `pyproject.toml`, `setup.py`, `requirements.txt`, or `poetry.lock` -> Selects `pytest` / `unittest`
  - Node.js: `package.json` -> Selects `npm test`, `jest`, or `vitest`
  - Rust: `Cargo.toml` -> Selects `cargo test`
  - Go: `go.mod` -> Selects `go test ./...`
- Verify that necessary dependencies or virtual environments are active or initialized.
- Output the target environment identifier and formulate the base command and arguments.

### Step 2: execute_test_suite [depends_on: discover_build_environment]
Execute the test command safely within the targeted project folder, tracking time elapsed and capturing stdout/stderr:
- Invoke the test execution command (e.g. `pytest --verbose` or `npm run test`) under a shell command runner.
- Enforce a strict execution timeout (default: 300 seconds) to prevent infinite loops, hung sockets, or zombie processes.
- Stream the stdout and stderr to temporary files or memory buffers, and capture the process exit code (where code `0` is typically a success, and non-zero is a failure).

### Step 3: compile_test_results [depends_on: execute_test_suite]
Parse execution outputs to extract structured metrics and present a comprehensive test quality scorecard:
- Parse the raw stdout/stderr logs of the runner using regex patterns to extract:
  - Total number of tests run
  - Count of passed tests
  - Count of failed tests
  - Count of skipped / pending tests
  - List of exact failing test names, filenames, line numbers, and their corresponding failure reasons or assertion errors.
- Construct a standardized JSON output object:
  - `status`: String ("PASSED", "FAILED", or "ERROR" if execution was blocked/timed out)
  - `metrics`: `{ total: Int, passed: Int, failed: Int, skipped: Int, duration_seconds: Float }`
  - `failures`: List of `{ test_name: String, file: String, line: Int, error_summary: String }`
- Output a clear, markdown-formatted summary report for inclusion in developer feedback loops or CI pipeline statuses.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| No manifest found | Target path is not a project root | Re-run `ls` on the correct root directory and pass that path to the runner |
| Status is ERROR with exit 124 | Suite exceeded the 300 second timeout | Re-run a narrower subset such as `pytest path/to/tests` and report the hanging test |
| Runner command not found | Dependencies or virtual environment not initialized | Install dependencies from the manifest (for example `pip install -e .` or `npm install`) and re-run |
| Totals do not add up | Output format differs from the regex patterns | Run the runner with its verbose or JSON reporter and parse that output |
