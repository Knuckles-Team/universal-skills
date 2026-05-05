# Standardized Grading Rubric

This document defines the 0–100 grading system used across all code-enhancer analysis domains.

## Grade Scale

| Grade | Score Range | Meaning | Emoji |
|-------|-------------|---------|-------|
| **A** | 90–100 | Excellent — meets or exceeds industry standards | 🟢 |
| **B** | 80–89 | Good — minor improvements possible | 🔵 |
| **C** | 70–79 | Acceptable — notable gaps exist | 🟡 |
| **D** | 60–69 | Below standard — significant issues | 🟠 |
| **F** | 0–59 | Failing — critical problems require immediate attention | 🔴 |

## Scoring Methodology

All domains start at **100 points** and apply **deductions** based on specific, evidence-backed findings. This deduction model ensures:

1. **Transparency** — Every point lost has a documented reason
2. **Reproducibility** — Same codebase produces same score on repeated runs
3. **Actionability** — Each deduction maps to a specific remediation action

## Per-Domain Rubrics

### Project Analysis (CE-001)
10 criteria × 10 points each = 100 max

| Criterion | Points | Evidence Required |
|-----------|--------|-------------------|
| pyproject.toml exists | 10 | File path |
| Project type detected | 10 | Ecosystem marker match |
| Externalized prompts | 10 | prompts/ directory listing |
| Observability tools | 10 | Dependency match (logfire, sentry, etc.) |
| Testing suite | 10 | tests/ dir + pytest dependency |
| AGENTS.md | 10 | File exists, >500 bytes for full credit |
| Pre-commit hooks | 10 | .pre-commit-config.yaml exists |
| .gitignore | 10 | File exists |
| Environment template | 10 | .env.example or .env.template exists |
| Protocol support | 10 | A2A/ACP/MCP indicators |

### Dependency Audit (CE-002)
Start at 100, deductions per outdated package:

| Status | Deduction | Reasoning |
|--------|-----------|-----------|
| Major version behind | -10 | Breaking changes likely, security risk |
| Minor version behind | -3 | New features missed, possible fixes |
| Patch version behind | -1 | Bug fixes, minor improvements |
| Package not on PyPI | -0 (warning) | May be private or renamed |

### Codebase Optimization (CE-003)
Thresholds based on industry standards (McCabe, Fowler):

| Metric | Threshold | Deduction |
|--------|-----------|-----------|
| Avg cyclomatic complexity > 10 | Severe | -15 |
| Avg cyclomatic complexity > 7 | Moderate | -8 |
| Long functions (>50 lines) > 10 | Many | -15 |
| Duplication ratio > 20% | High | -15 |
| Deep nesting (>4 levels) > 5 | Many | -10 |

### Security Analysis (CE-004)
Severity-weighted deductions per finding:

| Severity | Deduction | Example |
|----------|-----------|---------|
| High | -15 | eval/exec usage, SQL injection, hardcoded secrets |
| Medium | -8 | Broken crypto, unsafe deserialization |
| Low | -3 | Try-except-continue, partial path |

### Test Coverage (CE-005)

| Metric | Condition | Deduction |
|--------|-----------|-----------|
| Test-to-source ratio | <0.3 | -20 |
| Tests without assertions | >5 | -15 |
| Intent diversity | <2 types | -10 |
| Doc-test drift | >5 items | -10 |

### Documentation & Governance (CE-006)

| Criterion | Weight | Deduction if Missing |
|-----------|--------|---------------------|
| README.md | 25 | -25 |
| AGENTS.md | 25 | -25 |
| docs/ directory | 10 | -10 |
| Broken references | 15 | -3 to -15 |
| LICENSE | 5 | -5 |
| CHANGELOG.md | 5 | -5 |

### Architecture & Design Patterns (CE-011)

| Criterion | Deduction |
|-----------|-----------|
| SRP violations | -5 per type (max -20) |
| No layer architecture | -15 |
| Low DI ratio (<10%) | -10 |
| Poor module organization | -10 |

### Concept Traceability (CE-008)

| Metric | Deduction |
|--------|-----------|
| No concepts at all | Score set to 30 |
| Low trace ratio (<30%) | -30 |
| >5 orphans | -15 |
| >5 drift items | -10 |
| Tests missing concept markers | -2 per test (max -20) |
| >20 functions missing concept docstrings | -10 |
| >10 functions missing concept docstrings | -5 |

### Pre-Commit Compliance (CE-015)

| Metric | Deduction |
|--------|-----------|
| No `.pre-commit-config.yaml` | Score set to 15 |
| `pre-commit` not installed | Score set to 30 |
| Timed out (>300s) | Score set to 40 |
| Failed hook | -5 per hook (max -50) |
| Outdated hook (pinned to hash / pre-1.0) | -3 per hook (max -15) |

> **Note**: Pytest hooks are automatically skipped — CE-016 handles test execution with richer analysis.

### Test Execution (CE-016)

| Metric | Condition | Deduction |
|--------|-----------|-----------|
| Pass rate | <50% | -40 |
| Pass rate | <70% | -25 |
| Pass rate | <90% | -10 |
| Pass rate | <95% | -5 |
| No tests found | — | Score set to 20 |
| No test executed | — | Score set to 25 |
| Execution errors/timeouts | Per error | -5 (max -15) |

Supported frameworks: pytest, go test, npm test, cargo test, maven, gradle.

### Directory Organization (CE-017)

| Metric | Condition | Deduction |
|--------|-----------|-----------|
| Files per directory | >40 (severely crowded) | -10 per dir (max -30) |
| Files per directory | >20 (crowded) | -5 per dir (max -25) |
| Max depth | <2 (too flat, >20 files) | -10 |
| Max depth | >8 (too deep) | -10 |
| Monolithic directory | >50% of all files | -15 |

### Language Ecosystem (CE-018)

Informational domain — **not scored**. Provides a `LanguageProfile` consumed by all downstream analyzers.

Detects: Python, Go, Node/TypeScript, Rust, Java/Kotlin, Ruby, C#.

### UI/UX Quality (CE-019)

Nielsen's 10 Usability Heuristics × 10 points each = 100 max.

| Heuristic | Web Check | TUI Check |
|-----------|-----------|-----------|
| Visibility of system status | Loading/progress indicators | Spinners, status bars |
| Match real world | Semantic HTML, natural labels | Natural command names |
| User control & freedom | Navigation, undo, cancel | Ctrl+C, exit, --dry-run |
| Consistency & standards | CSS vars, component reuse | Color scheme, key bindings |
| Error prevention | Form validation, confirmations | Input validation, --dry-run |
| Recognition vs recall | Breadcrumbs, visible nav | Tab completion, suggestions |
| Flexibility & efficiency | Responsive, keyboard nav | Shortcuts, config files |
| Aesthetic & minimal design | Whitespace, color system | Aligned output, tables |
| Error recovery | Error boundaries, toasts | stderr, exit codes |
| Help & documentation | Tooltips, help pages | --help, man pages |

If no UI is detected, the domain is scored as **N/A** and excluded from GPA.

### Multi-Project Orchestration (CE-020)

Meta-domain — runs all analysis domains across multiple projects in parallel.

- Individual project reports maintain their own domain grades
- Unified comparison table ranks projects by GPA
- Cross-project SDD handoff aggregates all findings

### Cross-Project Integration (CE-021)

| Metric | Deduction |
|--------|-----------|
| Version conflict (major) | -5 per conflict (max -25) |
| Circular dependencies | -15 |
| Unused internal dependencies | -3 per dep (max -15) |
| No integration detected | N/A (not scored for standalone) |

### Agent Skill Quality (CE-026)

Weighted category model (skill-check scoring):

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Frontmatter | 30% | Required fields, naming conventions, field order |
| Description | 30% | Length, "Use when" phrasing, anti-trigger phrases |
| Body | 20% | Line/token limits, section structure |
| Links | 10% | Local markdown resolution, reference resolution |
| File/Meta | 10% | Trailing newlines, duplicate names/descriptions |

Per-skill: errors deduct 1× category weight, warnings deduct 0.5×.
Domain aggregate = mean of all per-skill scores.
If no skills detected: **N/A** (excluded from GPA).

See `references/skill_quality_rubric.md` for the full rule reference.

### Engineering Heuristics (CE-027)

Contextually activated — only active categories are scored:

| Category | Weight | Source Books | Activated When |
|----------|--------|-------------|----------------|
| H1: Construction Quality | 20% | Clean Code, Code Complete | Always |
| H2: Architecture Boundaries | 15% | Clean Architecture, Philosophy of Software Design | >5 modules or arch dirs |
| H3: Refactoring Discipline | 10% | Refactoring, Working Effectively with Legacy Code | Always |
| H4: Domain Modeling | 10% | DDD, DDD Distilled, Implementing DDD | DDD patterns detected |
| H5: Production Resilience | 15% | Release It!, DDIA | Service/API deps detected |
| H6: Enterprise Patterns | 10% | PoEAA | Enterprise dirs detected |
| H7: Engineering Practice | 20% | The Pragmatic Programmer | Always |

Active category weights are normalized to 100%.  Each category starts at 100
and applies deductions per failed heuristic.

See `references/engineering_heuristics.md` for the full check reference.

## Justification Requirements

Every grade MUST include:
1. **Criterion name** — What was evaluated
2. **Points awarded/deducted** — Numeric impact
3. **Evidence** — File path, line number, or command output
4. **Reasoning** — Human-readable explanation of why points were given or deducted
