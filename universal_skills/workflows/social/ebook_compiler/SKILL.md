---
name: ebook_compiler
description: Parallel execution workflow for ebook compiler using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-stirlingpdf
---

# Parallel Workflow: Ebook Compiler

This workflow defines the topological parallel execution steps for ebook compiler.

## Steps

### Step 1: outline
Execute the outline phase for the ebook_compiler workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: outline_artifacts
### Step 2: parallel_chapter_writing [depends_on: outline]
Execute the parallel chapter writing phase for the ebook_compiler workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_chapter_writing_artifacts
### Step 3: edit [depends_on: parallel_chapter_writing]
Execute the edit phase for the ebook_compiler workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: edit_artifacts
### Step 4: format [depends_on: edit]
Execute the format phase for the ebook_compiler workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: format_artifacts
### Step 5: epub_export [depends_on: format]
Execute the epub export phase for the ebook_compiler workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: epub_export_artifacts
