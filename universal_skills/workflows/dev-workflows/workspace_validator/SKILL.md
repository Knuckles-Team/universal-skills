---
name: workspace_validator
description: Agent workflow for validating the workspace using repository-manager MCP tools, fixing issues concurrently across all projects until 0 errors remain, and optionally bumping versions and pushing. Use when the user asks to validate projects, run repository-manager validation, fix all project errors, or ensure all projects are valid.
domain: development
tags: ['validation', 'workspace', 'repository-manager', 'bugfix', 'workflow', 'dev-workflows']
requires: ['repository-manager-mcp']
---

# workspace_validator Workflow

Autonomous workflow for systematically validating all projects in the workspace, reviewing and fixing the identified issues concurrently, and optionally publishing updates.

## ⚠️ Error Resolution Policy

> **CRITICAL:** When fixing validation errors, you MUST follow these rules:
>
> 1. **NEVER prefix variables with an underscore (`_`) to silence linting errors.** This is strictly prohibited. Renaming `var` to `_var` is not a fix — it's hiding the problem.
> 2. **Always determine root cause.** For every error, understand how the variable, implementation, or code was *intended* to function. Close the knowledge gap before making changes.
> 3. **Fix the real problem.** If a variable is unused because a feature is incomplete, complete the implementation. If it's genuinely dead code, remove it entirely — don't rename it.
> 4. **Troubleshoot ALL errors.** Every single error in the report must be understood and resolved at its root cause. No exceptions.

---

### Step 0: user-interaction
Clarify with the user if they only want to validate and fix issues, or if they also want to perform a phased bump (e.g. minor version) and phased push once 0 issues are found.
Expected: run_parameters

### Step 1: repository-manager-mcp
Submit validation using the `rm_projects` tool with `action="validate"`. If the user requested a phased bump and phased push, pass `auto_bump=true`, `auto_push=true`, and the requested `bump_part` parameter. This ensures the ecosystem will automatically bump and publish on the very first run if 0 issues are found. Store the reports in `/home/apps/workspace/reports`.
Expected: job_id
Depends On: Step 0

### Step 2: repository-manager-mcp
Poll for validation results by calling `rm_projects` with `action="validate_status"` and `job_id="<the-returned-id>"`. While polling is active, do NOT wait idle. Dynamically inspect the output directory `/home/apps/workspace/reports/validation-reports-<ts>/` for newly created project results subdirectories (e.g. `wger-agent-results/`). As soon as a repository folder is created and populated with its project summary `summary_<repo_underscores>_<ts>.md`, immediately read it to get a quick, actionable peek into the validation issues and start triaging and fixing that project's failures concurrently without waiting for the overall validation run to complete.
Expected: initial_validation_report
Depends On: Step 1

### Step 3: repository-manager-mcp
Enter remediation loop. Run automated remediation via `rm_workspace` with `action="remediate"`, coordinate manual fixes following the strict Error Resolution Policy, and validate targeted projects using the "Next Validation Command" from the report. As new validation sweeps run, continue utilizing dynamic per-project summaries to rapidly triage and fix bugs for completed repositories on-the-fly.
Expected: remediation_loop_completed
Depends On: Step 2

### Step 4: repository-manager-mcp
Execute the final regression sweep on all repositories (no targeted filtering) and verify that the report shows 0 failures.
Expected: final_regression_sweep_passed
Depends On: Step 3

### Step 5: repository-manager-mcp
If bumping and pushing was approved, verify that every project is on the `main` branch, run a minor version bump via `rm_workspace` with `action="maintain"`, and push via `rm_git` with `action="phased_push"`.
Expected: push_and_publish_results
Depends On: Step 4

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — user-interaction; Step 1 — repository-manager-mcp; Step 2 — repository-manager-mcp; Step 3 — repository-manager-mcp; Step 4 — repository-manager-mcp; Step 5 — repository-manager-mcp

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
