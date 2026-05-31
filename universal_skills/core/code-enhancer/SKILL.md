---
name: code-enhancer
description: >-
  Comprehensive code analysis and enhancement skill that performs 28-domain deep-
  dive reviews of any codebase. Covers project analysis, dependency audit,
  changelog audit, codebase optimization, security analysis, test coverage, pytest
  quality grading, test execution, pre-commit compliance, documentation
  governance, directory organization, language detection, UI/UX heuristics,
  architecture review, concept traceability, linting, vulnerability scanning,
  environment variable scanning, brainstorming, multi-project orchestration,
  cross-project integration, and actionable reporting with standardized 0-100
  grading and SDD handoff integration. Language-agnostic: supports Python, Go,
  Node, Rust, Java. Use when tasked with "auditing", "optimizing", "updating",
  "improving", "reviewing", "grading", or "enhancing" an agent, repository, or
  codebase. Replaces self-improver.
license: MIT
tags: [analysis, optimization, security, audit, grading, architecture, testing, documentation, traceability, linting, dependencies, sdd, pre-commit, ui-ux, multi-project, integration, changelog, pytest, env-vars]
metadata:
  author: Genius
  version: '0.35.0'
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
2.  **Dependency Audit** — Scan `pyproject.toml` and `requirements.txt`, check for latest versions on PyPI, flag outdated/deprecated/yanked packages.
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

## Steps

### Step 1: detect_language
Language ecosystem detection. Auto-detect primary/secondary languages, build system, available linters, and test frameworks to adapt downstream analysis:
- Requires: primary script `scripts/detect_language.py`

### Step 2: project_analysis [depends_on: detect_language]
Project structure and pattern analysis. Identify if the project is an MCP server, Pydantic-AI agent, library, or web application. Scan for architectural patterns, externalized prompts, and dependencies:
- Requires: primary script `scripts/analyze_project.py` and `scripts/audit_dependencies.py`

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
Concept traceability with drift detection. Scan for CONCEPT ID markers in code docstrings, docs, and pytest markers to cross-reference against AGENTS.md concepts:
- Requires: primary script `scripts/trace_concepts.py` and `scripts/audit_concept_ids.py`

### Step 9: user_interface_analysis [depends_on: project_analysis]
UI/UX heuristic evaluation. Detect web/terminal UI, run Nielsen's 10 usability heuristic checks, and execute WCAG AA accessibility checks:
- Requires: primary script `scripts/analyze_ui.py`

### Step 10: generate_report [depends_on: run_linters, run_tests, deep_code_analysis, security_analysis, documentation_audit, concept_traceability_audit, user_interface_analysis]
Consolidated graded report generation and SDD handoff. Compile findings, calculate 0-100 scores across 28 domains, and produce the final prettified code enhancement report and SDD-compatible TODOs:
- Requires: primary script `scripts/generate_report.py`, `scripts/generate_sdd_handoff.py`, `scripts/grade_pytest.py`, `scripts/grade_skills.py`, `scripts/evaluate_heuristics.py`, `scripts/detect_circular_deps.py`, `scripts/audit_env_var_standard.py`

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
- `scripts/detect_language.py` — Language ecosystem detection (CE-018)
- `scripts/analyze_project.py` — Project structure and pattern analysis (FR-001)
- `scripts/audit_dependencies.py` — PyPI dependency audit with version comparison (FR-002)
- `scripts/analyze_codebase.py` — Code quality, complexity, and duplication analysis (FR-003)
- `scripts/analyze_security.py` — Security and vulnerability scanning (FR-004, FR-010)
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
- `scripts/detect_circular_deps.py` — Circular dependency detection in pyproject.toml graphs (CE-028)
- `scripts/audit_concept_ids.py` — CONCEPT ID parity and collision detection across projects (CE-029)
- `scripts/audit_env_var_standard.py` — Env var naming standardization audit (CE-030)

### References
- `references/grading_rubric.md` — Standardized scoring criteria and justification templates
- `references/security_checklist.md` — CWE/STRIDE/OWASP reference for security analysis
- `references/architecture_patterns.md` — Industry patterns (hexagonal, SOLID, event-driven)
- `references/optimization_methodology.md` — Code smell taxonomy and remediation patterns
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
