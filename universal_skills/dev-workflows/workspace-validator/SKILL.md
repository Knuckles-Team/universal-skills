---
name: workspace-validator
description: >-
  Agent workflow for validating the workspace using repository-manager MCP tools, fixing issues concurrently across all projects until 0 errors remain, and optionally bumping versions and pushing. Use when the user asks to validate projects, run repository-manager validation, fix all project errors, or ensure all projects are valid.
license: MIT
tags: [validation, workspace, repository-manager, bugfix, workflow]
metadata:
  author: Genius
  version: '0.3.0'
---
# Workspace Validator

This skill defines the autonomous workflow for systematically validating all projects in the workspace, reviewing and fixing the identified issues concurrently, and optionally publishing updates. Validation runs as a **background job** — the `rm_projects` tool returns a `job_id` immediately, and you poll for results using `action="validate_status"`.

## ⚠️ Requirements
- Ensure the `repository-manager` MCP server is active so you have access to `rm_projects`, `rm_git`, and `rm_workspace` tools.
- DO NOT use the CLI `repository-manager` command for validation. You must use the MCP tools to optimize token usage and avoid reading large text report files.

## ⚠️ Error Resolution Policy

> **CRITICAL:** When fixing validation errors, you MUST follow these rules:

1. **NEVER prefix variables with an underscore (`_`) to silence linting errors.** This is strictly prohibited. Renaming `var` to `_var` is not a fix — it's hiding the problem.
2. **Always determine root cause.** For every error, understand how the variable, implementation, or code was *intended* to function. Close the knowledge gap before making changes.
3. **Fix the real problem.** If a variable is unused because a feature is incomplete, complete the implementation. If it's genuinely dead code, remove it entirely — don't rename it.
4. **Troubleshoot ALL errors.** Every single error in the report must be understood and resolved at its root cause. No exceptions.

## Workflow Instructions

### Phase 1: Clarification
1. When triggered, first clarify with the user if they only want to validate and fix issues, or if they *also* want to perform a phased bump (e.g. minor version) and phased push once 0 issues are found.
2. If not specified by the user, the default behavior is to ONLY validate and fix. Do not proceed to bumping/pushing unless explicitly confirmed.

### Phase 2: Initial Validation (Async Job Queue)
3. For the **first run**, submit validation using the `rm_projects` MCP tool with `action="validate"` and `type="all"`. You MUST pass `output_dir="/home/apps/workspace/reports"` to store the validation reports. DO NOT write to `/tmp` or any path outside the workspace. Do NOT pass the `repositories` parameter on the first run — validate all projects. Do NOT pass `coverage=true` unless the user explicitly requests code coverage.
4. The tool will return immediately with a `job_id`. **Do NOT wait idle.** While validation runs in the background, you can begin examining the codebase, reviewing recent changes, or preparing for remediation.
5. **Poll for results & triage on-the-fly:** Call `rm_projects` with `action="validate_status"` and `job_id="<the-returned-id>"`. Keep polling (with reasonable intervals) until `status` is `"completed"`.
   - **CRITICAL:** Do NOT wait for the entire validation to complete before acting. During polling, check the `<report_root>/` folder (where `<report_root>` is the sub-folder named `validation-reports-<timestamp>` inside `/home/apps/workspace/reports/`).
   - As each project's scan finishes, a folder `<project>-results/` will be dynamically created containing only `installation-*.md`, `pre-commit-results-*.md` (if failures occurred), and finally a single `summary_<repo_underscores>_<timestamp>.md` file.
   - **Immediately read** the project-specific `summary_<repo_underscores>_<timestamp>.md` file to identify validation errors for that project, and start triaging and fixing them in parallel while the main validation job is still running. This completely eliminates wait times!
6. Once the main validation job is complete, read the global `summary.md` in the top level of `<report_root>/` to review any remaining failures and ensure all project summaries have been processed.

### Phase 3: Remediation Loop (Command-Driven)

You will enter a continuous loop of fixing issues, then running the exact command specified in the report's `summary.md` or `index.md` file.

7. **Automated Remediation:** For systemic validation failures (such as `check-bumpversion` mismatches or simple `end-of-file-fixer` issues), you should use the native automated fix logic. Call the `rm_workspace` tool with `action="remediate"` and optionally pass the `repositories` parameter.
8. **Manual Fixes:** For any remaining issues (e.g. static analysis, failing tests), you MUST ALWAYS first come to understand the root cause by understanding how the variable, implementation, or code should have functioned, closing that knowledge gap. Follow the **Error Resolution Policy** above strictly. Note: Never automatically inject `# nosec` or `# noqa` for static analysis—evaluate manually and fix properly or suppress carefully.
9. Work on fixing the identified issues concurrently across different projects.
10. **Execute the Next Command from the Report:** After applying fixes, open the latest `index.md` report file. At the top of the report, there is a **"🔄 Next Validation Command"** section that contains the exact `rm_projects` MCP tool parameters to use for the next iteration. **Execute that command exactly as specified** — do NOT manually construct the parameters. The report auto-generates the correct `repositories` filter targeting only the previously failed projects.
11. Each subsequent validation call also returns a `job_id`. Poll with `validate_status` as in Phase 2, and continue monitoring and triaging newly generated per-repository `summary_<repo_underscores>_<timestamp>.md` files dynamically.
12. Review the new report. If there are still failures, repeat from step 7. Continue this loop until the report shows 0 failures.

### Phase 4: Final Regression Sweep

13. When the targeted validation shows 0 errors, the `index.md` will display a **"✅ Targeted Validation Passed — Run Full Regression Sweep"** section. This contains the command to run validation against ALL repositories (no `repositories` parameter). **Execute that command exactly as specified.**
14. If the full sweep passes with 0 errors, the report will show **"✅ All Repositories Passed — Validation Complete"**. Only at this point do you progress to the next phase.
15. If the full sweep reveals new regressions, return to Phase 3 step 7 and repeat the remediation loop.

### Phase 5: Bump and Push (Optional)
16. If the user confirmed in Phase 1 that they want to bump and push:
    a. **CRITICAL:** Before running any bumpversion logic, call the `rm_workspace` tool with `action="list_branches"`. Verify that every single project is currently on the `main` branch. If any project is on a different branch, you MUST stop and ask the user how to proceed, or align them back to `main` before bumping. Do NOT commit bumps to the wrong branches.
    b. Run the `rm_workspace` tool with `action="maintain"` and `part="minor"` to perform a phased bump to the next minor version.
    c. If the bump is successful, run the `rm_git` tool with `action="phased_push"` or `push` to push all projects back to github.
