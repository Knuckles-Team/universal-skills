---
name: strategy_code_review
description: Loads strategy script files, audits logic for lookahead bias, checks index variables leaks, and generates quality reviews.
domain: finance
tags: [code-review, static-analysis, leakage-bias, qa]
---
# Strategy Code Review Workflow

This workflow coordinates multi-agent parallel executions of Loads strategy script files, audits logic for lookahead bias, checks index variables leaks, and generates quality reviews.

### Step 1: strategy-parser [depends_on: none]
Loads strategy code files and extracts methods and properties.
Expected: strategy-abstract-syntax-tree

### Step 2: static-logic-reviewer [depends_on: strategy-parser]
Audits trading logic for common bugs (like lookahead bias, divide-by-zero).
Expected: logic-anomaly-records

### Step 3: leak-detector [depends_on: static-logic-reviewer]
Tests execution logic for information leakage or bad indexing.
Expected: information-leakage-verdicts

### Step 4: quality-report-compiler [depends_on: leak-detector]
Compiles performance and security review report.
Expected: strategy-review-dashboard

