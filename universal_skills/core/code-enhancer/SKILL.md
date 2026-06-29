---
name: code-enhancer
description: >-
  Comprehensive code analysis and enhancement skill that performs 31-domain deep-
  dive reviews of any codebase. Covers project analysis, dependency audit,
  changelog audit, codebase optimization, security analysis, test coverage, pytest
  quality grading, test execution, pre-commit compliance, documentation
  governance, directory organization, language detection, UI/UX heuristics,
  architecture review, concept traceability, linting, vulnerability scanning,
  environment variable scanning, runtime and scale profiling (memory, startup,
  instances-per-GB), brainstorming, multi-project orchestration,
  cross-project integration, and actionable reporting with standardized 0-100
  grading and SDD handoff integration. Language-agnostic: supports Python, Go,
  Node, Rust, Java. Use when tasked with "auditing", "optimizing", "updating",
  "improving", "reviewing", "grading", or "enhancing" an agent, repository, or
  codebase. Replaces self-improver.
license: MIT
tags: [analysis, optimization, security, audit, grading, architecture, testing, documentation, traceability, linting, dependencies, sdd, pre-commit, ui-ux, multi-project, integration, changelog, pytest, env-vars, profiling]
metadata:
  author: Genius
  version: '1.0.0'
---

# Code Enhancer

This skill enables the agent to perform a comprehensive, multi-domain "Code Enhancement Review"
of any codebase. It produces a prettified, graded report with standardized 0–100 scoring across
28 analysis domains, actionable TODOs prioritized by impact and risk, and structured SDD handoff
for implementation.

Supports **language-agnostic** analysis for Python, Go, Node/TypeScript, Rust, and Java projects.
Can run against **multiple projects in parallel** for cross-repository integration analysis.

## Capabilities

1.  **Project Analysis** — Scan for architectural patterns, externalized prompts, and observability integrations.
2.  **Dependency Audit, Update & Migration** — Scan `pyproject.toml` and `requirements.txt`, check for latest versions on PyPI, flag outdated/deprecated/yanked packages, **APPLY version bumps** (lossless rewrite of constraint floors/caps, `--level {patch,minor,major}`, dry-run by default) via `apply_dependency_updates.py` (CE-042), **and surface migration impact** — new features to adopt and deprecated/removed APIs our code must drop — via `analyze_dependency_migration.py` (CE-043), including a pytest-driven `DeprecationWarning` capture mode.
3.  **Codebase Optimization** — Apply industry-proven methodologies: system discovery, structural smell identification, feature classification, duplication analysis, dependency boundary establishment, and incremental optimization patterns.
4.  **Security Analysis** — Conduct defensive security analysis: attack surface discovery, dependency/CVE exposure assessment, CWE-centric codebase analysis, threat modeling, input flow analysis, authentication/authorization review, and operational security hardening.
5.  **Test Coverage Analysis** — Perform pytest use-case coverage analysis: test inventory, use-case mapping, coverage dimension analysis (line, feature, risk), test intent classification, and drift detection between docs and tests.
6.  **Documentation & Governance** — Audit README.md (industry-standard grading), AGENTS.md, and `/docs`: validation techniques, taxonomy establishment, lifecycle management, and automated drift detection.
7.  **Brainstorming** — Provide structured ideation for UI/UX enhancements and architectural upgrades.
8.  **Concept Traceability** — Implement executable documentation with bidirectional traceability using stable concept IDs embedded in code docstrings, docs, and pytest markers (including `@pytest.mark.concept()` decorators), with drift detection, registry cross-reference, and missing-marker detection.
9.  **Linting & Formatting** — Execute language-appropriate linters (ruff/mypy/bandit for Python, go vet for Go, eslint for Node). Parse and categorize findings.
10. **Vulnerability Scanning** — Integrate bandit, pip-audit, and repository-manager validation. Consolidate into unified vulnerability register.
11. **Architecture & Design Patterns** — Evaluate against industry patterns (hexagonal/clean architecture, SOLID principles, event-driven orchestration) and find deepening opportunities to turn shallow modules into deep ones. Conduct conversational architectural reviews based on ADRs and domain glossary.
12. **Actionable Reporting** — Generate consolidated report with specific TODOs, prioritized by impact and risk, with SDD handoff for implementation.
13. **Pre-Commit Compliance** — Run `pre-commit run --all-files`, detect outdated hooks, parse per-hook pass/fail. Smart pytest deduplication (pytest hooks skipped → CE-016 handles them).
14. **Test Execution** — Detect test framework (pytest, go test, npm test, cargo test, maven, gradle), execute tests with 300s timeout, grade based on pass/fail ratio.
15. **Directory Organization** — Measure files-per-directory density, detect crowded/monolithic structures, suggest logical reorganization into subdirectories.
16. **Language Ecosystem Detection** — Auto-detect primary/secondary languages, build system, available linters, and test frameworks. Adapts all downstream analysis.
17. **UI/UX Quality** — Grade web and terminal UIs using Nielsen's 10 Usability Heuristics via static file analysis. WCAG 2.1 AA accessibility checks for web projects.
18. **Multi-Project Orchestration** — Run all analysis domains across multiple projects in parallel with configurable concurrency. Per-project reports + unified cross-project summary.
19. **Cross-Project Integration** — Analyze inter-project dependency graphs, detect version conflicts, circular dependencies, and unused internal dependencies.
20. **README Grading** — Industry best-practice scoring for README.md: title, badges, description, ToC, installation, usage, architecture, contributing, license, code blocks, docs references, broken links, length, env var docs, MCP tool tables, deployment docs.
21. **Changelog Audit** — Validate CHANGELOG.md against Keep a Changelog standard using `keepachangelog` library. Check version drift against pyproject.toml, analyze dependency changelogs for version deltas (new features, breaking changes, deprecations, security fixes).
22. **Pytest Quality Grading** — Grade pytest suites against F.I.R.S.T. rubric: naming quality, structure/organization, fixture/parametrize usage, assertion quality, and AI slop detection (duplicate bodies, over-mocking, generic names).
23. **Environment Variable Scanning** — Scan Python source, Dockerfiles, compose.yml, .env/.env.example for all env var usage. Cross-reference against README documentation to identify undocumented variables.
24. **Agent Skill Quality** — Auto-detect SKILL.md files in any repository and grade them using a rule engine ported from skill-check: frontmatter validation, description quality, body structure, link resolution, and duplicate detection. Contextual — only activates when skills are present.
25. **Engineering Heuristics** — Evaluate codebase against battle-tested principles synthesized from 13 industry-standard software engineering books (Clean Code, Clean Architecture, Refactoring, The Pragmatic Programmer, Release It!, DDIA, DDD, and more). Uses contextual activation — domain modeling rules only fire when DDD patterns are detected; production resilience rules only fire for service/API projects.
26. **Circular Dependency Detection** — Scan `pyproject.toml` dependency graphs across workspace projects for circular or transitive resolution cycles. Detect workspace member conflicts and optional-dependency self-references.
27. **CONCEPT ID Parity** — Verify that every project has a `docs/concepts.md` with a unique prefix, cross-reference CONCEPT IDs in docs against code annotations, detect orphaned or undocumented concepts, and verify no prefix collisions across the ecosystem.
28. **Environment Variable Standardization Audit** — Check `auth.py` files across all agents for non-standard env var naming patterns (e.g., `_VERIFY` vs `_SSL_VERIFY`, `_BASE_URL` vs `_URL`, `_INSTANCE` vs `_URL`). Flag duplicates within the same project and deviations from the ecosystem standard.

29. **Intent & Opportunity Discovery** — Infer the codebase's intent (README/docs/entrypoints) and surface value-add opportunities in three tiers: low-hanging fruit (capabilities built but not exposed/wired), implied-but-missing (partial CRUD lifecycles, stubs), and net-new intent-aligned features. Answers *what could this become?*, not just *what's broken?*
30. **Runtime Profiling** — Measure what a single running instance actually costs: import-time resident memory, startup wall time, and the heaviest transitive imports (via `-X importtime`), profiling the console-script entry module rather than the bare package. Flags heavy dependencies (ML runtimes, browser engines) loaded unconditionally into every process. Budget-scored on RSS and startup. **Opt-in** (executes the target).
31. **Scale Profiling** — Spawn N idle instances concurrently, sample real resident memory, and report per-instance footprint, instances-per-GB density, and a projection across common RAM sizes (1/2/4/8 GB) — answers *how many of these fit on a Raspberry Pi / small node?* **Opt-in** (executes the target; never runs in the default sweep).

## Grading System

All domains are scored 0–100 using standardized criteria:

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90–100 | Excellent — meets or exceeds industry standards |
| B | 80–89 | Good — minor improvements possible |
| C | 70–79 | Acceptable — notable gaps exist |
| D | 60–69 | Below standard — significant issues |
| F | 0–59 | Failing — critical problems require immediate attention |

Every grade includes a justification with specific file paths and evidence citations.

## Headless & KG-Native Operation (60-repo scale)

For batch/CI use across many repositories, prefer the headless driver over running the 11 agent
steps by hand:

```bash
# 1. Validate the toolchain before a batch (smoke-runs every analyzer on a fixture)
python scripts/selftest.py                       # exits non-zero if any script is broken

# 2. Analyze ONE repo headlessly — language-gated, per-domain timeout + fault isolation,
#    incremental JSON written as each domain completes (CE-031)
python scripts/enhance_repo.py /path/to/repo --out reports/ --kg

# 3. Ingest the run into graph-os via the MCP (best-effort; skips cleanly with no endpoint) (CE-032)
GRAPH_OS_MCP_URL=http://localhost:8000 python scripts/kg_ingest_run.py reports/repo.enhance.json

# 4. Cross-repo + bi-temporal questions the KG answers but a filesystem tool can't (CE-034)
python scripts/kg_query_runs.py list                          # the cross-repo Cypher library
python scripts/kg_query_runs.py query regressions            # via graph-os MCP
python scripts/kg_query_runs.py deltas --current reports/ --prior reports_prev/   # offline diff
```

- **`enhance_repo.py`** is the per-repo unit; `run_multi_project.py` fans it out across repos with
  `-c` concurrency. Domains not applicable to the detected primary language are skipped (a Python
  dependency audit does not run on a Rust repo).
- **KG-native** ingest/query talk to the **graph-os MCP server over HTTP**, never via a direct
  `import agent_utilities.*` (that hard dependency previously broke the KG step). Each run is
  time-stamped so the KG's bi-temporal layer surfaces per-repo score deltas over time.
- Every new script supports `--self-test`; `selftest.py` aggregates them plus a fixture run of every
  analyzer.

## Steps

### Step 1: detect_language
Language ecosystem detection. Auto-detect primary/secondary languages, build system, available linters, and test frameworks to adapt downstream analysis:
- Requires: primary script `scripts/detect_language.py`

### Step 2: project_analysis [depends_on: detect_language]
Project structure and pattern analysis. Identify if the project is an MCP server, Pydantic-AI agent, library, or web application. Scan for architectural patterns, externalized prompts, and dependencies:
- Requires: primary script `scripts/analyze_project.py` and `scripts/audit_dependencies.py` (write path: `scripts/apply_dependency_updates.py`)

### Step 3: run_linters [depends_on: detect_language]
Language-aware linter orchestration. Execute language-appropriate linters (ruff, mypy, bandit for Python, go vet for Go, eslint for Node) and parse/categorize findings:
- Requires: primary script `scripts/run_linters.py` and `scripts/run_precommit.py`

### Step 4: run_tests [depends_on: detect_language]
Multi-framework test execution and grading. Execute detected test framework with a 300s timeout and grade based on the pass/fail ratio:
- Requires: primary script `scripts/run_tests.py`

### Step 5: deep_code_analysis [depends_on: project_analysis]
Code quality, complexity, and duplication analysis. Measure cyclomatic complexity, function length, nesting depth, duplicate blocks, monolithic files, and module coupling:
- Requires: primary script `scripts/analyze_codebase.py` and `scripts/analyze_directory_density.py`

### Step 6: security_analysis [depends_on: project_analysis]
Security and vulnerability scanning. Discover attack surface, scan for CWE patterns, scan environment variables/credentials, and parse vulnerability reports:
- Requires: primary script `scripts/analyze_security.py` and `scripts/scan_env_vars.py`

### Step 7: documentation_audit [depends_on: project_analysis]
Documentation governance and drift detection. Validate README/AGENTS.md, check for documentation staleness, verify KEEP_A_CHANGELOG standards, and detect drift against code:
- Requires: primary script `scripts/audit_documentation.py` and `scripts/audit_changelog.py`

### Step 8: concept_traceability_audit [depends_on: project_analysis]
Concept traceability with drift detection. Scan for CONCEPT ID markers in code docstrings, docs, and pytest markers, and cross-reference against the canonical concept registry (`docs/concepts.yaml`/`concepts.yml` or `AGENTS.md`). Concept-ID parity/collision detection is folded into this script:
- Requires: primary script `scripts/trace_concepts.py`

### Step 9: user_interface_analysis [depends_on: project_analysis]
UI/UX heuristic evaluation. Detect web/terminal UI, run Nielsen's 10 usability heuristic checks, and execute WCAG AA accessibility checks:
- Requires: primary script `scripts/analyze_ui.py`

### Step 10: generate_report [depends_on: run_linters, run_tests, deep_code_analysis, security_analysis, documentation_audit, concept_traceability_audit, user_interface_analysis]
Consolidated graded report generation and SDD handoff. Compile findings, calculate 0-100 scores across 28 domains, and produce the final prettified code enhancement report and SDD-compatible TODOs:
- Requires: primary script `scripts/generate_report.py`, `scripts/generate_sdd_handoff.py`, `scripts/grade_pytest.py`, `scripts/grade_skills.py`, `scripts/evaluate_heuristics.py`

### Step 11: kg_persistence [depends_on: generate_report]
Knowledge Graph double-write seeding and multi-project analysis. Ingest the report and spec files back into Graph-OS, and execute multi-project parallel cross-repository integration checks:
- Requires: primary script `scripts/run_multi_project.py` and `scripts/analyze_integration.py`

## Best Practices
- **Read-Only First**: Always provide the report and wait for user approval before applying destructive changes or major refactors.
- **Evidence-Backed Findings**: Every recommendation, finding, or proposed change MUST be backed by hard evidence retrieved from the Knowledge Graph using the `agent-utilities-kg` MCP server (e.g., `kg_query`, `kg_search`). You must cite specific file paths, exact line numbers, and existing graph topologies. Never hallucinate recommendations; the KG is your source of truth.
- **Extend-Before-Invent**: When suggesting new features or modules, first use `kg_analogy_search` or `kg_search` to verify if a relevant concept already exists. Always prefer extending an existing conceptual module over inventing a duplicate.
- **Wire or Discard**: Implementations must adhere to the Wire-First heuristic (≤3 hops from an entry point). If a feature cannot be wired directly into a hot path or duplicates an existing concept (Similarity ≥ 0.7), it must be extended or discarded. Dead code is prohibited. When recommending architectural changes or creating implementation handoffs, ensure that the proposed code is fully wired into the system architecture's run path (the "hot path") and does not remain a disconnected stub.
- **Holistic Documentation & Testing**: All SDD handoffs and generated TODOs MUST explicitly require updates to `CHANGELOG.md`, `AGENTS.md`, `README.md`, codebase docstrings, `/docs` (including overview pages and architectural diagrams), and `pytests`. Architecture diagrams are critical for building agent context.
- **Ecosystem Focus**: Prioritize standards defined in `agent-utilities` (e.g., loading prompts from `prompts/*.md`).
- **Context Awareness**: Scale recommendations to project size. Do not suggest complex graph architectures for small projects.
- **Assumption Validation**: Validate all assumptions before taking them at face value. Check actual file contents, run commands, verify paths.
- **SDD Dual-Write Integration**: Output reports, TDD specs, and domain designs to the `.specify/` directory structure for compatibility with the SDD toolset. The repository's `.specify/` folder MUST be treated as the **Single Source of Truth**. After generating or modifying any files in the `.specify/` folder, you MUST immediately invoke the `kg_ingest` MCP tool against the `.specify/` directory to sync these changes into the unified Knowledge Graph. This dual-write ensures complete ecosystem parity.
- **XDG Standard Compliance**: For any repository that writes files (logs, configuration, data), automatically verify that it stores these files in the XDG recommended standard locations (`~/.local/share/<app>`, `~/.config/<app>`, `~/.cache/<app>`). Report any violations (e.g. `~/.appname/`) as codebase optimization action items and patch them when permitted.
- **Smart Deduplication**: Pytest hooks in pre-commit are automatically skipped — CE-016 provides richer test analysis.
- **Language Awareness**: Always run `detect_language.py` first to adapt analysis to the project's ecosystem.
- **Per-Project .specify**: When running multi-project analysis, SDD handoffs go to each individual project's `.specify/` folder (e.g., `agents/github-agent/.specify/`), NOT the parent directory. Remember to `kg_ingest` each project's `.specify/` folder after updates.

## Bundled Resources

### Scripts
- `scripts/enhance_repo.py` — **Headless single-repo driver**: runs all applicable domains for one
  repo, language-gated, per-domain timeout + fault isolation, incremental output (CE-031)
- `scripts/kg_ingest_run.py` — KG-native ingest of a run into graph-os via the MCP (CE-032)
- `scripts/kg_query_runs.py` — Cross-repo + bi-temporal queries over runs (CE-034)
- `scripts/selftest.py` — Toolchain self-test harness; smoke-runs every analyzer (CE-033)
- `scripts/analyze_opportunities.py` — **Intent & Opportunity Discovery**: infers codebase intent, surfaces low-hanging-fruit / implied-missing / net-new value-adds (CE-035)
- `scripts/analyze_runtime_profile.py` — **Runtime Profiling**: import RSS, startup wall time, heaviest transitive imports, heavy-dependency flags; budget-scored (CE-036, opt-in)
- `scripts/analyze_scale_profile.py` — **Scale Profiling**: spawns N idle instances, reports per-instance footprint + instances-per-GB density projection (CE-037, opt-in)
- `scripts/analyze_liveness.py` — **Liveness / Dead Pathways**: detects code that exists but is never wired into a running path, via three deterministic layers (CE-038): (1) *static reachability* — orphan modules + never-referenced top-level defs; (2) *dynamic liveness* — functions never executed across the test suite, read from a `coverage.py` JSON (`--coverage coverage.json`) — catches "reachable but never invoked"; (3) *typed-seam / contract drift* — public functions returning an untyped `dict`/`list[dict]` (the seam where producer/consumer key contracts silently drift, e.g. a producer writing `_score` while the consumer reads `score` → `0.00`) plus (4) *facade detection* — live-surface handlers (MCP tool / API route / CLI command) that return a canned payload doing NO real work (the 'invoked-but-fake' class, incl. per-branch facades inside a real dispatcher) and admitted placeholder/stub markers (TODO/FIXME/mock/'for now'/sample data). No LLM — runs unattended on CI/cron; with `--baseline base.json` it exits non-zero on any regression (ratchet gate).
- `scripts/detect_language.py` — Language ecosystem detection (CE-018)
- `scripts/analyze_project.py` — Project structure and pattern analysis (FR-001)
- `scripts/audit_dependencies.py` — PyPI dependency audit with version comparison (FR-002)
- `scripts/apply_dependency_updates.py` — **Dependency update application** (CE-042): the *write* path to the audit. Bumps `pyproject.toml`/`requirements.txt` constraint floors/caps to PyPI-latest, losslessly (only version operands change; extras/markers/comments/order preserved). `--level {patch,minor,major}`, `--apply` (default dry-run diff), `--only/--skip`, `--self-test`. Excludes the project's own self-referential extras and never pins to a pre-release. Reuses `audit_dependencies._get_latest_version`. Opt-in via `enhance_repo.py --apply-deps LEVEL`.
- `scripts/analyze_dependency_migration.py` — **Dependency migration intelligence** (CE-043): answers *what's new to adopt* and *what's deprecated to remove* after a bump. Per upgradable package it (a) mines the changelog Added/Deprecated/Removed across the crossed version range (reuses `audit_changelog` helpers) and intersects Deprecated/Removed with the symbols our code imports (via `importlib.metadata.packages_distributions`), and (b) **`--pytest PATH`** runs the suite under `DeprecationWarning` capture (the highest-yield signal — catches e.g. a dep's `'openai:'`→`'openai-chat:'` v2 rename that only fires at runtime), splitting our-code deprecations (fix) from forward-looking dependency ones (review before next major). `--run` for an import-only scan; `--self-test`.
- `scripts/analyze_codebase.py` — Code quality, complexity, and duplication analysis (FR-003)
- `scripts/analyze_security.py` — Security and vulnerability scanning (FR-004, FR-010)
- `scripts/analyze_minimalism.py` — **Minimalism / over-engineering audit** (CE-040): deterministic ponytail "lazy senior dev" lens — flags commented-out code (`delete:`), trivial wrapper functions (`yagni:`), and shrinkable expressions (`shrink:`), ranked biggest-cut-first with a `net: -N lines possible` estimate, and counts `ponytail:`/`upgrade-path:` marked shortcuts. No LLM.
- `scripts/analyze_baseline.py` — **Baseline-aware new-debt gate** (CE-039): fingerprints findings (line- and count-independent) and diffs a run against a saved snapshot → `new`/`persisting`/`fixed`, so CI can fail only on *new* debt. Used by `enhance_repo.py --baseline/--write-baseline` and `generate_report.py --baseline`.
- `scripts/analyze_tests.py` — Test coverage and intent classification (FR-005)
- `scripts/audit_documentation.py` — Documentation governance and drift detection (FR-006)
- `scripts/analyze_architecture.py` — Architecture pattern evaluation (FR-011)
- `scripts/trace_concepts.py` — Concept traceability with drift detection (FR-008)
- `scripts/run_linters.py` — Language-aware linter orchestration (FR-009)
- `scripts/run_precommit.py` — Pre-commit compliance and hook freshness (CE-015)
- `scripts/run_tests.py` — Multi-framework test execution and grading (CE-016)
- `scripts/analyze_directory_density.py` — Directory organization analysis (CE-017)
- `scripts/analyze_ui.py` — UI/UX heuristic evaluation (CE-019)
- `scripts/run_multi_project.py` — Multi-project parallel orchestration (CE-020)
- `scripts/analyze_integration.py` — Cross-project integration analysis (CE-021)
- `scripts/analyze_version_sync.py` — Version synchronization and drift detection (CE-022)
- `scripts/generate_report.py` — Consolidated graded report generation (FR-012, FR-013)
- `scripts/generate_sdd_handoff.py` — SDD-compatible TODO generation (FR-014)
- `scripts/audit_changelog.py` — Changelog validation and dependency delta analysis (CE-023)
- `scripts/grade_pytest.py` — Pytest quality grading with F.I.R.S.T. rubric (CE-024)
- `scripts/scan_env_vars.py` — Environment variable scanning and documentation check (CE-025)
- `scripts/grade_skills.py` — Agent skill quality grading with skill-check rule engine (CE-026)
- `scripts/evaluate_heuristics.py` — Engineering heuristics evaluation from 13 books (CE-027)
- `scripts/analyze_liveness.py` — Liveness / dead-pathway + facade detection (CE-038)
- `scripts/analyze_opportunities.py` — Intent & opportunity discovery (CE-035)
- `scripts/analyze_runtime_profile.py` / `scripts/analyze_scale_profile.py` — runtime & scale profiling (CE-036/CE-037, opt-in)
- `scripts/findings_filter.py` — Deterministic security false-positive filter (CE-041)

> CONCEPT-ID parity/collision detection (CE-028/CE-029) and env-var-standardization (CE-030) are folded into `trace_concepts.py` and `scan_env_vars.py` respectively — there are no separate `detect_circular_deps.py` / `audit_concept_ids.py` / `audit_env_var_standard.py` scripts.

### References
- `references/grading_rubric.md` — Standardized scoring criteria and justification templates
- `references/security_checklist.md` — CWE/STRIDE/OWASP reference for security analysis
- `references/architecture_patterns.md` — Industry patterns (hexagonal, SOLID, event-driven)
- `references/optimization_methodology.md` — Code smell taxonomy and remediation patterns
- `references/minimalism-ladder.md` — Lazy-first ladder (YAGNI → stdlib → native → existing dep → one line) and the `ponytail:`/`upgrade-path:` marked-shortcut convention; the discipline `analyze_minimalism.py` audits and that generation/refactor should follow (CE-040)
- `references/profiling_methodology.md` — Runtime/scale profiling budgets, scoring, per-language tool matrix, and the heavy-import failure mode (CE-036/CE-037)
- `references/report_template.md` — Prettified report template with Mermaid and table patterns
- `references/ui_heuristics.md` — Nielsen's heuristics, WCAG criteria, SUS reference
- `references/integration_patterns.md` — Cross-project dependency and interface patterns
- `references/changelog_standard.md` — Keep a Changelog 1.1.0 format reference and validation criteria
- `references/pytest_rubric.md` — F.I.R.S.T. rubric, AI slop detection criteria, organization best practices
- `references/skill_quality_rubric.md` — Agent skill grading rules, scoring model, and attribution
- `references/engineering_heuristics.md` — Unified heuristic framework from 13 books with architecture flow diagram
- `references/DEEPENING.md` — Strategies for creating deep modules
- `references/INTERFACE-DESIGN.md` — Principles for designing testable, deep interfaces
- `references/LANGUAGE.md` — Architectural domain language and terminology
- `references/evolution_log.md` — **Skill feedback loop**: dated, evidence-anchored record of every rubric tuning / false-positive fix / new capability, citing the domain output that prompted it. When a run surfaces a false positive, a miss, or an over/under-harsh score, add an entry here AND make the corresponding fix — this is how the skill evolves from observation rather than guesswork.
