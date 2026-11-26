---
name: code-walkthrough
domain: development
skill_type: skill
description: Generates code walkthroughs
license: MIT
tags: []
metadata:
  version: '1.6.2'
  author: Knuckles-Team
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

## Steps

1. Locate the target path and list its entry points.
   Run `ls -R <path> | head -50` and `grep -rn "def main\|if __name__" <path>`. Verify that at least one entry point or public module is identified.
2. Identify the core components and read each one.
   Use `grep -rn "^class \|^def " <path>` to enumerate them. Verify that every component you will describe has a file and line reference.
3. Trace the data flow from entry point to output.
   Use `grep -rn "<function name>" <path>` to follow each call. Verify that each hop in the narrative maps to a real call site.
4. Write the linear markdown walkthrough with file and line links.
   Save it as `walkthrough.md`. Verify that `grep -c "\.py:\|:L[0-9]" walkthrough.md` is nonzero and that each cited line range exists via `sed -n '<a>,<b>p' <file>`.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Walkthrough cites lines that no longer match | Code changed after reading, or line numbers were guessed | Reopen the file with `sed -n` for the range, correct the reference, and re-check each citation |
| Narrative skips a component | Entry points were not fully enumerated | Rerun the `grep` for classes and functions, add the missing component, and re-trace the data flow |
| Path is too large to cover | Scope too broad | Ask the user to narrow to one package or feature and walk that subtree only |
