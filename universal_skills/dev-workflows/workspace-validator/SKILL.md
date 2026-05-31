---
name: workspace-validator
description: >-
  Agent workflow for validating the workspace using repository-manager MCP tools, fixing issues concurrently across all projects until 0 errors remain, and optionally bumping versions and pushing. Use when the user asks to validate projects, run repository-manager validation, fix all project errors, or ensure all projects are valid.
license: MIT
tags: [validation, workspace, repository-manager, bugfix, workflow]
metadata:
  author: Genius
  version: '0.4.0'
---
# Workspace Validator

This skill defines the autonomous workflow for systematically validating all projects in the workspace, reviewing and fixing the identified issues concurrently, and optionally publishing updates. Validation runs as a **background job** per repository using `rm_projects`. The tool returns a job dictionary immediately, and you poll for results using `action="validate_status"`.

## ⚠️ Requirements
- Ensure the `repository-manager` MCP server is active so you have access to `rm_projects`, `rm_git`, and `rm_workspace` tools.
- DO NOT use the CLI `repository-manager` command for validation. You must use the MCP tools to optimize token usage.
- **NEVER manually edit pyproject.toml versions, commit, tag, or push releases.** All maintenance must be driven automatically via the `repository-manager` using the `auto_bump` and `auto_push` parameters.
- **Topological Release Order (`CONCEPT:RM-TOPOLOGY`):**
  - **Phase 3:** `agent-utilities` must be bumped and published first.
  - **Phase 4:** Core Tools & UIs (including `geniusbot`, `agent-terminal-ui`, `agent-webui`, `universal-skills`, `skill-graphs`) consume `agent-utilities`. Bumping `agent-utilities` triggers automated dependency updates in Phase 4 projects.
  - Circular dependencies are prevented by the `repository-manager` skipping dependency updates for any project belonging to a phase lower than the currently bumped phase.

## ⚠️ Error Resolution Policy

> **CRITICAL:** When fixing validation errors, you MUST follow these rules:

1. **NEVER prefix variables with an underscore (`_`) to silence linting errors.** This is strictly prohibited. Renaming `var` to `_var` is not a fix — it's hiding the problem.
2. **Always determine root cause.** For every error, understand how the variable, implementation, or code was *intended* to function. Close the knowledge gap before making changes.
3. **Fix the real problem.** If a variable is unused because a feature is incomplete, complete the implementation. If it's genuinely dead code, remove it entirely — don't rename it.
4. **Troubleshoot ALL errors.** Every single error in the report must be understood and resolved at its root cause. No exceptions.

## 🧪 Poison Pill Detection

> **CRITICAL:** Before starting any validation run, be aware of **workspace-level cascading failures**.

The root `pyproject.toml` uses `uv` workspace globs (e.g. `agent-packages/agents/*`) to include all projects. If **any single project** in that glob has a malformed or missing `pyproject.toml`, the entire workspace resolution fails. This causes **every** project's pytest phase to report the same error:

```
error: Workspace member `/path/to/broken-project` is missing a `pyproject.toml`
```

**Detection:** If the `rm_projects` JSON results show the exact same error message across many or all projects pointing at a single workspace member, that project is the "poison pill".

**Resolution:**
1. Navigate to the broken project directory.
2. Verify its `pyproject.toml` exists and is valid PEP 517 compliant:
   - Must have `[build-system]` with `build-backend = "setuptools.build_meta"` (NOT `build_meta`).
   - Must have a `[project]` section with `name` and `version`.
3. Fix or create the `pyproject.toml`, then re-run validation.
4. **Do NOT waste time fixing individual project pytest errors when the root cause is a poison pill.** Fix the pill first; the cascading errors will disappear.

## Workflow Instructions

### Phase 1: Clarification
1. When triggered, first clarify with the user if they only want to validate and fix issues, or if they *also* want to perform a phased bump (e.g. minor version) and phased push once 0 issues are found.
2. If not specified by the user, the default behavior is to ONLY validate and fix. Do not proceed to bumping/pushing unless explicitly confirmed.

### Phase 2: Parallel Validation
3. For the **first run**, submit validation using the `rm_projects` MCP tool with `action="validate"`. Do NOT pass the `repositories` parameter on the first run — validate all projects.
4. The tool now runs asynchronously in the background and immediately returns a job submission confirmation.
5. **Poll for Progress:** Call the `rm_projects` tool with `action="validate_status"`. The tool returns an enriched JSON object containing:
   - `running_projects`: Array of repository names still being validated.
   - `failed_projects_csv`: A comma-separated string of repositories that failed validation (perfect for re-feeding into `validate`).
   - `jobs`: Array of job detail objects (each containing `repo_name`, `status`, and `summary`).
6. **Analyze the Return:** As soon as a job finishes, if it failed, its `summary.failures` will contain the exact hook failure messages. You can use the `failed_projects_csv` field to immediately identify failures and use `jq` on the tool's raw output file to extract the exact hook failures for those projects without waiting for the entire sweep to finish!
7. **Monitor:** Continue polling `validate_status` (with reasonable intervals) until `running_projects` is empty.

### Phase 3: Remediation Loop
You will enter a continuous loop of fixing issues based on the JSON hook outputs.

8. **Automated Remediation:** For systemic validation failures (such as simple formatting issues), you should use the native automated fix logic. Call the `rm_workspace` tool with `action="remediate"`.
9. **Manual Fixes:** For any remaining issues (e.g. static analysis, failing tests), follow the **Error Resolution Policy** above strictly. Fix issues concurrently across different projects.
10. **Re-Validate Specific Projects:** After applying fixes to specific repositories, call `rm_projects(action="validate", repositories="repo1,repo2")` targeting ONLY the projects you fixed or that previously failed.
11. Review the new structured JSON. If there are still failures, repeat from step 8. Continue this loop until the target repositories pass.

### Phase 4: Final Regression Sweep & Release
12. When the targeted validation shows 0 errors, run validation against ALL repositories one last time. If the user confirmed in Phase 1 that they want to bump and push, you can cascade this final run into a release by calling `rm_projects` with `action="validate"`, `auto_bump=true`, and `auto_push=true`. Do not pass the `repositories` parameter.
13. **CRITICAL:** Before running any validation with `auto_bump=true`, call the `rm_workspace` tool with `action="list_branches"`. Verify that every single project is currently on the `main` branch. If any project is on a different branch, you MUST stop and ask the user how to proceed, or align them back to `main` before validating with the bump flag.
14. The backend will now orchestrate the entire sequence in a single background job. Poll `action="validate_status"` until the job completes. The results will contain the validation summary, and if successful, the `bump` and `push` release results.
15. If the full sweep passes and the release occurs, you are done. If new validation regressions are revealed, the bump/push will be safely aborted by the backend, and you must repeat the remediation loop.
