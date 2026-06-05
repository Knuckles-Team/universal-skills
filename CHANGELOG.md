# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`research/comparative-analysis` — Lightweight Mode + CA→SDD inner loop.** Optimized the skill
  for repeated code-vs-code innovation extraction. New **Innovation Ledger** artifact bridges
  comparative analysis to SDD, plus six self-testing scripts: `pin_source.py` (CA-017, source
  pin/incremental/cache), `verify_claims.py` (CA-013, marketing-vs-code gate), `parse_concept_registry.py`
  (CA-012, offline Extend-Before-Invent), `score_recommendations.py` (CA-015, leverage/effort/risk +
  build order + success-metric enforcement), `ledger_to_sdd.py` (CA-014, scaffolds `.specify/`
  design/spec/tasks), and `check_wiring.py` (CA-016, runnable ≤3-hop import-graph wiring audit). Added
  `references/innovation_ledger_schema.md` and `references/exploration_return_schema.md`; SKILL.md gains
  a Mode Selection section (Lightweight default vs Deep/KG), an enforced pre-flight, and mode-conditional
  steps. The pipeline is `pin → explore→ledger → verify → score → scaffold-SDD → wiring-audit`.

### Fixed
- `research/comparative-analysis/scripts/check_wiring.py` — **plugin-registration awareness**: a module nothing imports directly but that self-registers via a decorator/registry (`@adaptor`, `register_source`, entry-points, `pkgutil` discovery) is no longer false-flagged as a Wire-First violation (`registered_via_plugin` in the result). Surfaced while auditing self-registering enrichment extractors.
- `research/comparative-analysis/scripts/check_wiring.py` — normalize ledger `target_module`
  paths (repo-root relative, e.g. `pkg/sub/mod.py`) by stripping the `--package` prefix so they
  match the `--root`-relative import-graph keys. Surfaced while dogfooding the memory-os analysis.
- `dev-workflows/diagnose` skill for structured debugging loops.
- `integration/issue-triage` skill for triaging GitHub issues via state machine.
- `system/zoom-out` skill for meta-level architectural reviews.
- `core/efficient-mode` skill for ultra-compressed communication (renamed from caveman).
- `research/research-scanner/scripts/dynamic_scorer.py` — Dynamic KG-aware relevance scoring that auto-detects agent-utilities concepts for taxonomy construction.
- `core/code-enhancer/scripts/analyze_xdg_kg.py` — XDG Knowledge Graph analysis script for deep code quality integration.

### Changed
- **`research/research-scanner`**: Refactored from monolithic `relevance_scanner.py` to an agent-driven workflow. The skill now extracts focus topics from the KG, dynamically builds relevance taxonomies, and orchestrates `scholarx` MCP tools for paper discovery. Updated SKILL.md with step-by-step agentic execution workflow.
- `core/code-enhancer`: Integrated architectural improvement capabilities (deepening opportunities, conversational review). Added `analyze_xdg_kg.py` script.
- `core/session-handoff`: Added multi-session handoff management and KG persistence context.
- `dev-workflows/c4-architecture`: Added KG-native concept traceability integration.
- `dev-workflows/diagnose`: Added structured state machine debugging loop patterns.
- `sdd/task-planner`: Integrated `to-issues` concepts (vertical slicing via tracer bullets, issue tracker syncing).
- `sdd/sdd-implementer`: Added KG-native task persistence and status tracking.
- `sdd/spec-generator`: Added optional issue tracker integration for generated specs.
- `dev-workflows/tdd-methodology`: Added "Horizontal Slices" anti-pattern guidelines.
- `research/brainstorming`: Added "Scrutiny Mode" for relentless requirement interviewing.
- `core/skill-builder`: Added exact description constraints (1024 char limit, structure).
- `research/comparative-analysis`: Expanded cross-domain innovation extraction and KG integration capabilities.
- `agent-tools/agent-package-builder`: Enhanced scaffold template generation for Docker, MCP, and A2A infrastructure.

### Removed
- `research/research-scanner/scripts/relevance_scanner.py` — Replaced by `dynamic_scorer.py` agentic workflow.

### Fixed
-

## [0.1.58] - 2026-04-29

### Added
- Initial release
