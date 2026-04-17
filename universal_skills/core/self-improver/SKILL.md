---
name: self-improver
description: Analyzes the current project/workspace for architectural improvements, performance optimizations, and provides a comprehensive report. It checks ALL project dependencies for potential updates and brainstorms design/UI enhancements based on modern standards. Use when tasked with "auditing", "optimizing", "updating", or "improving" an agent or repository.
tags: [analysis, optimization, updates, audit, self-improvement, architecture]
version: '0.1.58'
---

# Self-Improver

This skill enables the agent to perform a deep-dive "Self-Improvement Review" of a codebase. It focuses on modern agentic standards (Agent-Utilities ecosystem), dependency health, and design excellence.

## Capabilities

1.  **Project Analysis**: Scans for patterns like Graph vs Flat agents, externalized prompts, and observability integrations.
2.  **Dependency Audit**: Scans `pyproject.toml` or `requirements.txt` and checks for the latest versions on PyPI.
3.  **Brainstorming**: Provides structured ideation for UI/UX enhancements and architectural upgrades.
4.  **Actionable Reporting**: Generates a consolidated "Self-Improvement Report" with specific TODOs.

## Agentic Workflow

### 1. Discovery & Analysis
- **Assess Structure**: Identify if the project is an MCP server, a Pydantic-AI agent, or a supporting library.
- **Run `analyze_project.py`**: Execute the bundled script to detect architectural patterns and missing features.
- **Check Dependencies**: Run `check_pypi_updates.py` to compare current versions against the latest stable releases on PyPI.

### 2. Strategy & Ideation
- **Reference Guidelines**: Read `references/improvement_checklist.md` to identify gaps in performance, security, or DX.
- **Brainstorm Design**: Evaluate the web interface (if any) against contemporary design aesthetics (glassmorphism, vibrant palettes, micro-animations).
- **Evaluate Architecture**: Suggest migrating complex tasks to `pydantic-graph` if currently using a simpler structure.

### 3. Reporting
- **Generate Report**: Create a markdown artifact titled `self_improvement_report.md`.
- **Categorize Findings**: Group by "Critical Updates", "Architectural Enhancements", "Performance Optimizations", and "Design/UX Brainstorming".
- **Prioritize**: Mark items as [Low], [Medium], [High] impact.

## Best Practices

- **Read-Only First**: Always provide the report and wait for user approval before applying destructive changes or major refactors.
- **Ecosystem Focus**: Prioritize standards defined in `agent-utilities` (e.g., loading prompts from `prompts/*.md`).
- **Context Awareness**: If the project is small, do not suggest overly complex graph architectures.

## Bundled Resources

### Scripts
- `scripts/analyze_project.py`: Scans for project types and structural patterns.
- `scripts/check_pypi_updates.py`: Queries PyPI for dependency updates.

### References
- `references/improvement_checklist.md`: Comprehensive quality gates for agentic software.
- `references/agent_utilities_standards.md`: Specific best practices for the current ecosystem.
