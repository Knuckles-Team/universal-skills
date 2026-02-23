---
name: project-planning
description: "High-level reasoning, brainstorming, debugging, research, evaluation, and project execution patterns. Use this before starting complex multi-step tasks to explicitly scaffold plans prior to execution."
categories: [Productivity]
tags: [planning, reasoning, debugging, research, guidelines, evaluation, brainstorming]
---

# Project Planning & Thinking Tools

## Overview

This capability provides scripts and documentation focused on Agentic reasoning, long-horizon planning, iterative evaluation, and systematic debugging. Use patterns and guidelines from the `docs/` directory when scaffolding major projects or trying to fix impossible bugs.

## Capabilities/Tools

### 1. Deep Research (`scripts/research.py`)
Performs iterative deep web-search to gather comprehensive documentation before starting complicated projects or when evaluating competing choices.
```bash
python scripts/research.py "Top 3 frameworks for LLM evaluation metrics in 2026"
```

### 2. Evaluation & Pipelines (`scripts/evaluator.py`, `scripts/pipeline_template.py`)
- Standard evaluators for validating output quality.
- Scaffolds for data pipelines to enforce consistency.

## Planning Guidelines (`docs/`)
We have aggregated standard operating procedures for agentic thinking:
- **Test-Driven Development (TDD)**: Write tests first before modifying implementation code. See `docs/testing-anti-patterns.md`.
- **Systematic Debugging**: See `docs/root-cause-tracing.md` and `docs/defense-in-depth.md` to stop guessing and start tracing.
- **Evaluating Artifacts**: See `docs/metrics-guide.md` to objectively score outputs.
- **Brainstorming**: Don't just pick the first option. Create a spectrum of alternatives, score them across different dimensions, and choose the optimal path.
