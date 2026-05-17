# Comparative Analysis Report Template

## Report: {title}
**Date**: {date}
**Mode**: {mode} (codebase|research|hybrid|innovation)
**Projects Analyzed**: {project_count}

## Executive Summary
{executive_summary}

## Architecture Topology

### {project_a} — Architecture Map
{c4_diagram_a}

**Entry Points**: {entry_point_count_a}
**Hot Path Coverage**: {hot_path_coverage_a}%
**Design Patterns**: {design_patterns_a}

### {project_b} — Architecture Map
{c4_diagram_b}

**Entry Points**: {entry_point_count_b}
**Hot Path Coverage**: {hot_path_coverage_b}%
**Design Patterns**: {design_patterns_b}

## Comparison Matrix

| Domain | {project_names} |
|--------|{column_dividers}|
| CA-001 Governance | {scores} |
| CA-002 Ecosystem Health | {scores} |
| CA-003 Architecture | {scores} |
| CA-003b Architecture Diff | {arch_diff_summary} |
| CA-004 Code Quality | {scores} |
| CA-005 Security | {scores} |
| CA-006 Testing | {scores} |
| CA-007 Documentation | {scores} |
| CA-008 Performance | {scores} |
| **Weighted GPA** | **{gpas}** |

## Radar Chart (Mermaid)

Use this template for visual comparison:

```mermaid
%%{init: {'theme': 'dark'}}%%
radar-beta
  title Comparative Analysis
  axis Governance, Health, Architecture, Quality, Security, Testing, Docs, Performance
  "{project_a}" : [{scores_a}]
  "{project_b}" : [{scores_b}]
```

## Architecture Differential

### Component Topology Gaps
Components in {source} but missing from {target}:
{component_gaps}

### Hot Path Comparison
| Metric | {source} | {target} |
|--------|----------|----------|
| Entry Points | {source_ep} | {target_ep} |
| Hot Path Coverage | {source_hp}% | {target_hp}% |
| Cold Modules | {source_cold} | {target_cold} |

### Design Pattern Divergence
{design_pattern_diff_table}

## Wiring Opportunities

Prioritized integration points where {target} should wire new features:

| Priority | Type | Component | Action | Wiring Hint |
|----------|------|-----------|--------|-------------|
{wiring_opportunities_rows}

## Design Decisions Required

Architectural conflicts that require human judgment:
{design_conflicts}

## Per-Domain Deep Dives

### CA-001: Governance
{governance_analysis}

### Winner Determination
For each domain, declare:
- **Winner**: Project with highest score
- **Delta**: Score difference
- **Key Differentiator**: What made the difference

## Innovation & Integration Potential
{innovation_section}

## Architecture Adherence Checklist

For each recommended feature, verify before implementation:

- [ ] **Entry Point Exists**: MCP tool, A2A skill, or API route exposes this
- [ ] **Engine Integration**: Feature callable from core engine or mixin
- [ ] **Hot Path Reachable**: Traceable from entry point in ≤3 hops
- [ ] **C4 Diagram Updated**: Component shown in architecture diagram
- [ ] **Concept Map Updated**: CONCEPT:ID present and accurate
- [ ] **Design Consistent**: Implementation follows sibling module patterns
- [ ] **Tests Exist**: At least one test exercises the hot path through this feature

## Recommendations
1. ...
2. ...

## Research Assimilation Tracking

After implementation, mark papers as assimilated:
```
kg_write(action='assimilate', article_path='<paper_id>.pdf', codebase='<target>', status='implemented')
```
