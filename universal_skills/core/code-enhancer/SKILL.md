---
name: code-enhancer
description: >-
  Comprehensive code analysis and enhancement skill that performs 23-domain deep-
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
  version: '0.10.0'
---

# Code Enhancer

This skill enables the agent to perform a comprehensive, multi-domain "Code Enhancement Review"
of any codebase. It produces a prettified, graded report with standardized 0–100 scoring across
23 analysis domains, actionable TODOs prioritized by impact and risk, and structured SDD handoff
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

## Agentic Workflow

### Phase 1: Discovery & Baseline
- **Detect Language**: Run `detect_language.py` to identify project ecosystem (Python/Go/Node/Rust/Java).
- **Assess Structure**: Identify if the project is an MCP server, Pydantic-AI agent, library, or web application.
- **Run `analyze_project.py`**: Detect architectural patterns and score against ecosystem standards.
- **Run `audit_dependencies.py`**: Compare current dependency versions against latest stable PyPI releases.
- **Run `run_linters.py`**: Execute language-appropriate linters against the target codebase.

### Phase 1.5: Tooling Execution
- **Run `run_precommit.py`**: Execute pre-commit hooks, detect outdated revs. Pytest hooks automatically skipped.
- **Run `run_tests.py`**: Execute detected test framework with 300s timeout. Grade pass/fail ratio.

### Phase 2: Deep Analysis
- **Run `analyze_codebase.py`**: Measure cyclomatic complexity, function length, nesting depth, duplication, monolithic files, and module coupling.
- **Run `analyze_security.py`**: Discover attack surface, scan for CWE patterns, parse vulnerability reports.
- **Run `analyze_tests.py`**: Inventory tests, map to use-cases, classify intent, detect doc-test drift, find missing concept markers.
- **Run `audit_documentation.py`**: Validate docs completeness, README industry grading, detect staleness, check drift against code.
- **Run `analyze_architecture.py`**: Evaluate against SOLID, hexagonal, clean architecture patterns.

### Phase 2.5: Structure Analysis
- **Run `analyze_directory_density.py`**: Measure files-per-directory, detect crowded/flat/deep structures, rogue scripts, suggest reorganizations.

### Phase 2.6: Changelog & Environment
- **Run `audit_changelog.py`**: Validate CHANGELOG.md format, check version drift, analyze dependency changelogs for version deltas.
- **Run `scan_env_vars.py`**: Scan all sources for env var usage, cross-reference against README documentation.
- **Run `grade_pytest.py`**: Grade pytest suite against F.I.R.S.T. rubric with AI slop detection.

### Phase 2.7: Skill Quality & Engineering Heuristics
- **Run `grade_skills.py`**: Discover and grade agent skills (if detected in Phase 1). Uses skill-check rule engine.
- **Run `evaluate_heuristics.py`**: Assess codebase against engineering book heuristics with contextual activation.

### Phase 3: Traceability & Governance
- **Run `trace_concepts.py`**: Scan for `CONCEPT:CE-XXX` markers in code docstrings, docs, pytest markers and decorators. Detect orphans, drift, and missing markers. Cross-reference against AGENTS.md concept registry.

### Phase 3.5: UI Analysis
- **Run `analyze_ui.py`**: Detect web/terminal UI, run Nielsen's 10 heuristic checks, WCAG accessibility audit for web.

### Phase 4: Brainstorming & Ideation
- **Reference Guidelines**: Read `references/` documents to identify gaps in performance, security, and DX.
- **Brainstorm Design**: Evaluate interfaces against contemporary design aesthetics.
- **Evaluate Architecture**: Suggest improvements based on industry patterns.

### Phase 5: Reporting & Handoff
- **Run `generate_report.py`**: Create prettified `code_enhancement_report.md` in `.specify/reports/`.
- **Run `generate_sdd_handoff.py`**: Produce structured TODO items compatible with `spec-generator` → `task-planner` → `sdd-implementer` pipeline. Output to `.specify/specs/`.
- **Categorize Findings**: Group by domain with graded scorecards.
- **Prioritize**: Sort action items by impact × risk composite score.

### Phase 6: Multi-Project (Optional)
- **Run `run_multi_project.py`**: Execute all phases across multiple projects in parallel.
- **Run `analyze_integration.py`**: Build inter-project dependency graph, detect version conflicts and circular deps.
- **Generate Unified Summary**: Cross-project comparison table ranked by GPA.

## Best Practices

- **Read-Only First**: Always provide the report and wait for user approval before applying destructive changes or major refactors.
- **Ecosystem Focus**: Prioritize standards defined in `agent-utilities` (e.g., loading prompts from `prompts/*.md`).
- **Context Awareness**: Scale recommendations to project size. Do not suggest complex graph architectures for small projects.
- **Assumption Validation**: Validate all assumptions before taking them at face value. Check actual file contents, run commands, verify paths.
- **SDD Integration**: Output reports to `.specify/` directory structure for compatibility with the SDD toolset (spec-kit standard). Each project gets its own `.specify/` folder — do NOT use the monorepo root.
- **Smart Deduplication**: Pytest hooks in pre-commit are automatically skipped — CE-016 provides richer test analysis.
- **Language Awareness**: Always run `detect_language.py` first to adapt analysis to the project's ecosystem.
- **Per-Project .specify**: When running multi-project analysis, SDD handoffs go to each individual project's `.specify/` folder (e.g., `agents/github-agent/.specify/`), NOT the parent directory.

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
