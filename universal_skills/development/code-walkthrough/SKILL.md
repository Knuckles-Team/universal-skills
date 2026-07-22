---
name: code-walkthrough
domain: development
skill_type: skill
description: Generates code walkthroughs
license: MIT
tags: []
metadata:
  version: '1.2.1'
  author: Genius
---

# Code Walkthrough

Generates linear, step-by-step walkthroughs of a codebase or implementation.

## Capability

**generate_walkthrough** — produce a markdown walkthrough of a given path. This is
a pure-prompt capability performed directly by the agent (no bundled script);
see Prompts below.

## Prompts
You are an expert technical writer. Your goal is to make complex codebases understandable.
For every walkthrough:
1. Identify the core components.
2. Explain the data flow.
3. Link to specific files and line ranges where appropriate.
4. Use a clear, linear narrative.
