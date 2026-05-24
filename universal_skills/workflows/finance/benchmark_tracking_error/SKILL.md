---
name: benchmark_tracking_error
description: Pulls daily benchmark indices, calculates active share tracking error, decomposes performance style, and dispatches drift alerts.
domain: finance
tags: [tracking-error, active-share, style-attribution, drift]
---
# Benchmark Tracking Error Workflow

This workflow coordinates multi-agent parallel executions of Pulls daily benchmark indices, calculates active share tracking error, decomposes performance style, and dispatches drift alerts.

### Step 1: benchmark-returns-collector [depends_on: none]
Fetches daily rolling returns logs for active holdings and indices.
Expected: benchmark-price-returns

### Step 2: tracking-error-calculator [depends_on: benchmark-returns-collector]
Computes rolling tracking error and active share indexes.
Expected: rolling-tracking-errors

### Step 3: return-attribution-engine [depends_on: tracking-error-calculator]
Decomposes portfolio returns into asset selection and style attribution.
Expected: style-returns-attribution

### Step 4: drift-alert-dispatch [depends_on: return-attribution-engine]
Checks target bounds and dispatches alerts on breach.
Expected: portfolio-drift-verdicts

