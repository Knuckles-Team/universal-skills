---
name: systems-manager
description: "Comprehensive codebase search, file navigation, and deep structural analysis using glob, ripgrep, and AST parsing."
categories: [System & Infrastructure, Development]
tags: [system, files, navigation, code, search, analysis, tree-sitter, grep]
---

# Systems Manager

## Overview

This skill encompasses tools and strategies for navigating directory structures, fast precise codebase search using `ripgrep`, and deep structural code analysis using Tree-Sitter and Abstract Syntax Trees (AST). These tools are the foundation for efficient agentic exploration.

## Capabilities / Tools

### 1. File Navigation Mapping (`ls`, `fd`, `tree`)
- **tree**: `tree -L 2` to understand high-level layout. Use `-I` to ignore noise.
- **fd (fd-find)**: A faster alternative to `find`. `fd -H` to include hidden, `fd -e <ext>` to filter.
- **ls**: Basic navigation with `ls -l` for permissions and size.

### 2. Fast Codebase Search (`rg`, `glob`)
- **ripgrep (rg)**: A fast line-oriented search tool respecting `.gitignore`.
  - *Example*: `rg "class User" -t py -n`
  - *Example*: `rg "TODO" -g "!tests/" -C 2`
  - *Flags*: `-n` (line numbers), `-i` (case insensitive), `-C` (context), `-t` (file type), `-g` (glob).
- **Glob Patterns**: Use `**/*.py` or `rg --files -g "**/*.{js,ts}"`.

### 3. Structural Code Analysis
- Use **Tree-Sitter** and **AST Traversal** for deep structural code analysis when simple regex search is insufficient.
- **Goal**: Find code elements based on syntactic structure (e.g., "all function definitions"), extract definitions, and walk the syntax tree hierarchy.
- **Usage**: Use `python` to load `tree-sitter` and run queries against the codebase. Combine with `ripgrep` to narrow down results first.

## Agentic Workflow

1.  **Assess Structure**: Use `tree -L 2` or `ls -R` to understand the layout.
2.  **Locate Files**: Use `glob` patterns and `fd` to find target files.
3.  **Precise Text Search**: Use `ripgrep` for specific symbols. Use context (`-C 2`) to understand usage.
4.  **Deep Analysis**: Fallback to Tree-Sitter python scripts when structural insights are required.
5.  **Understand**: Read the identified file contents for complete context.

## Best Practices
- **Prefer `rg` over `grep`**: Always use `ripgrep` for its speed and `.gitignore` honoring.
- **Limit Depth**: Always cap depth (`-L` or `-maxdepth`) when exploring large repositories.
- **Filter Early**: Use `-I` or `.gitignore` to skip `node_modules`, `venv`, etc.
