---
name: comparative-analysis
description: >-
  Comprehensive multi-modal comparative analysis engine for codebases, research papers,
  and cross-domain innovation extraction. Evaluates governance, architecture, quality,
  security, testing, docs, and performance.
license: MIT
tags: [analysis, comparison, evaluation, benchmark, architecture, security, governance, research, innovation, biomimicry, analogical-reasoning, TRIZ, maturity, license, compliance, enterprise, grading, radar-chart]
metadata:
  author: Genius
  version: '0.9.0'
---

# Comparative Analysis

Multi-modal comparative analysis engine that evaluates and compares any combination of
codebases and research papers across 56+ industry-standard metrics organized into 8
analysis domains. Supports innovation extraction via biomimicry, analogical reasoning,
TRIZ inventive principles, and emergent value discovery.

## Analysis Modes

This skill operates in **4 modes** depending on the inputs:

| Mode | Inputs | Primary Value |
|------|--------|---------------|
| **Codebase vs Codebase(s)** | 2+ project directories | Enterprise maturity comparison |
| **Codebase vs Research** | Project dir + paper files | Innovation integration potential |
| **Research vs Research** | 2+ paper/document files | Novelty and approach comparison |
| **Innovation Extraction** | Any source + target codebase | Hidden value-add discovery |

## Workflow

### Phase -1: KG-Backed Discovery (Optional — CONCEPT:KG-2.12)

When `agent-utilities` Knowledge Graph is available, sources can be resolved
directly from the KG instead of requiring filesystem paths. This enables
comparisons against previously ingested research papers, codebases, and
knowledge bases without manual file management.

```bash
# Discover KG sources matching a query
python scripts/discover_projects.py --kg-query "multi-agent orchestration"

# Combine KG sources with filesystem paths
python scripts/discover_projects.py --kg-query "knowledge graph" /path/to/project1

# KG resolution is optional — if agent-utilities is not installed, it gracefully skips
```

KG sources are materialized to `~/.scholarx/analysis/` as markdown files with
embedded metadata for downstream analysis scripts.

### Phase 0: Discovery & Classification

1. Run `scripts/discover_projects.py` with all target paths to classify each input as
   `codebase` or `research` and detect language ecosystems.
2. The script auto-determines the analysis mode based on input types.
3. If mode is ambiguous, ask the user to clarify intent.

```bash
python scripts/discover_projects.py /path/to/project1 /path/to/project2
python scripts/discover_projects.py https://github.com/example/repo /local/project
python scripts/discover_projects.py --mode research /path/to/paper1.md /path/to/paper2.md
```

If Git URLs are provided, the script will automatically clone them into a temporary directory (`.specify/ca_repos/<session_id>`) using `repository-manager` and substitute the URL with the local cloned path in the output JSON.

### Phase 1: Governance Analysis (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_governance.py /path/to/project > results/project_ca001.json
```

Evaluates: License type and OSI compliance, contributor diversity and bus factor,
governance files (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, CODEOWNERS).

Read `references/license_compatibility.md` for license tier classification if the
user asks about license compatibility between projects.

### Phase 2: Ecosystem Health (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_ecosystem_health.py /path/to/project > results/project_ca002.json
```

Evaluates: Git commit frequency and recency, release cadence and SemVer adherence,
CI/CD pipeline presence, dependency freshness and pinning rates.

### Phase 3: Architecture & Design (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_architecture.py /path/to/project > results/project_ca003.json
```

Evaluates: Protocol support (MCP, A2A, ACP, REST, gRPC, GraphQL), type annotation
coverage, module structure and nesting depth, 12-Factor compliance signals.

Read `references/architecture_patterns.md` for pattern detection criteria if needed.

### Phase 4: Code Quality (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_code_quality.py /path/to/project > results/project_ca004.json
```

Evaluates: Cyclomatic complexity (McCabe), code duplication percentage, stub/TODO/FIXME
density, function length distribution, dead code indicators.

### Phase 5: Security & Compliance (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_security.py /path/to/project > results/project_ca005.json
```

Evaluates: OWASP Top 10 pattern exposure, CWE anti-pattern density, hardcoded secret
detection, input validation coverage, auth framework presence.

Read `references/security_standards.md` for OWASP/CWE detection pattern reference.

### Phase 6: Testing & Reliability (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_testing.py /path/to/project > results/project_ca006.json
```

Evaluates: Test suite presence and framework, test count and test-to-code ratio,
testing pyramid shape (unit > integration > e2e), quality indicators (fixtures,
parametrize, markers, timeouts).

### Phase 7: Documentation & DX (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_documentation.py /path/to/project > results/project_ca007.json
```

Evaluates: README completeness (15 criteria), docstring coverage percentage,
documentation artifacts (docs/, CHANGELOG, CONTRIBUTING, examples/).

### Phase 8: Performance & Cost (Codebase mode only)

Run for each codebase project:
```bash
python scripts/analyze_performance.py /path/to/project > results/project_ca008.json
```

Evaluates: Benchmark suite presence, dependency count and weight, async/concurrency
adoption ratio, container configuration.

### Phase 9: Innovation Extraction (All modes)

Run when comparing research papers to codebases or discovering cross-domain innovations:
```bash
python scripts/extract_innovations.py --source /path/to/paper.md --target /path/to/codebase
python scripts/extract_innovations.py --sources /path/to/paper1.md /path/to/paper2.md
```

Applies 5 methodologies:
1. **Biomimicry Pattern Matching** — Maps nature-inspired concepts to software patterns
2. **Analogical Reasoning (Structure Mapping)** — Transfers relational structures across domains
3. **TRIZ Inventive Principles** — Systematic contradiction resolution
4. **Emergent Value Discovery** — Identifies "free" capabilities from integration
5. **First Principles Decomposition** — Reconstructs novel combinations from primitives

Read `references/innovation_extraction.md` for full methodology details.

### Phase 10: Report Generation

Generate the unified comparison report:
```bash
python scripts/generate_comparison_report.py results/*.json --output report.md
```

For codebase analysis, output to `.specify/reports/comparative_analysis.md`.
For research-only analysis, ask the user where to save the report (default: current
working directory). The user may specify paths like `~/Documents/`.

### Phase 11: Cleanup (If Applicable)

If Git URLs were provided in Phase 0, `discover_projects.py` will output a `cleanup_instruction` in the JSON and print a terminal warning.
After successfully generating the comparison report in Phase 10, **you must delete the temporary directory** containing the cloned repositories to free up workspace space:
```bash
rm -rf /home/apps/workspace/.specify/ca_repos/<session_id>
```

## Output Location Rules

1. **Codebase analysis** involving a primary project → `.specify/reports/comparative_analysis.md`
   inside that project directory
2. **Multi-codebase** with no primary → output to the workspace root or user-specified path
3. **Research-only analysis** → ask user for preferred output location (suggest `~/Documents/`)
4. **Innovation extraction** → same directory as the target codebase's `.specify/reports/`
5. Always support `--output <path>` override for any mode

## Grading System

All domains scored 0–100 with consistent grading:

| Grade | Score | Meaning |
|-------|-------|---------|
| A+ | 95–100 | Exceptional — industry-leading |
| A | 90–94 | Excellent — exceeds enterprise standards |
| B+ | 85–89 | Very Good — minor refinement opportunities |
| B | 80–84 | Good — solid foundation |
| C+ | 75–79 | Above Average — meets minimum standards |
| C | 70–74 | Acceptable — significant gaps |
| D | 60–69 | Below Standard — major issues |
| F | 0–59 | Failing — critical problems |

Read `references/grading_rubric.md` for detailed scoring criteria per domain, including
research paper scoring dimensions and innovation extraction scoring.

## Best Practices

- **Run Phase 0 first** to auto-detect mode and avoid running irrelevant analyzers
- **Save intermediate JSON results** so the report generator can be re-run without re-analysis
- **Read-only analysis**: Never modify the target projects. Only read and report.
- **Context-aware depth**: Scale analysis depth to project size. Small projects may score
  lower on governance/CI simply due to scale — note this in recommendations.
- **Innovation extraction is always valuable**: Even in pure codebase comparisons, run
  Phase 9 between codebases to discover hidden synergies and emergent value.
- **Ask before expensive operations**: If a project is very large (>100k LOC), warn the
  user that analysis may take longer and offer to skip heavy domains.

## Bundled Resources

### Scripts
- `scripts/discover_projects.py` — CA-000: Input classification and metadata extraction
- `scripts/analyze_governance.py` — CA-001: License, ownership, bus factor analysis
- `scripts/analyze_ecosystem_health.py` — CA-002: Git activity, releases, CI, deps
- `scripts/analyze_architecture.py` — CA-003: Protocols, types, modules, 12-Factor
- `scripts/analyze_code_quality.py` — CA-004: Complexity, duplication, stubs, length
- `scripts/analyze_security.py` — CA-005: OWASP/CWE patterns, secrets, auth posture
- `scripts/analyze_testing.py` — CA-006: Test suite, coverage, pyramid, quality
- `scripts/analyze_documentation.py` — CA-007: README grading, docstrings, artifacts
- `scripts/analyze_performance.py` — CA-008: Benchmarks, deps, async, containers
- `scripts/extract_innovations.py` — CA-010: Biomimicry, analogical reasoning, synergies
- `scripts/generate_comparison_report.py` — CA-009: Unified report with radar charts

### References
- `references/grading_rubric.md` — Scoring criteria for all domains and modes
- `references/industry_frameworks.md` — CHAOSS, DORA, OWASP, 12-Factor, SOLID, ISO 25010
- `references/license_compatibility.md` — OSI/SPDX compatibility matrix and risk tiers
- `references/architecture_patterns.md` — Clean/hexagonal/modular pattern detection
- `references/security_standards.md` — CWE/OWASP detection patterns and scoring
- `references/innovation_extraction.md` — Biomimicry, TRIZ, Structure Mapping methodology
- `references/report_template.md` — Markdown comparison report template
