---
name: portfolio_stress_test
description: Aggregates return curves, runs historical crash scenarios, computes rate shock exposures, and compiles risk audits.
domain: finance
tags: [stress-test, crash, scenario-analysis, risk]
---
# Portfolio Stress Test Workflow

This workflow coordinates multi-agent parallel executions of Aggregates return curves, runs historical crash scenarios, computes rate shock exposures, and compiles risk audits.

### Step 1: returns-data-crawlers [depends_on: none]
Gathers historical holdings and benchmarks returns data.
Expected: historical-stress-pricing-data

### Step 2: scenario-crash-simulator [depends_on: returns-data-crawlers]
Simulates returns during historical financial crisis events.
Expected: crisis-returns-scenarios

### Step 3: interest-rate-shock [depends_on: returns-data-crawlers]
Applies simulated treasury yield spikes to active pricing metrics.
Expected: interest-rate-shock-scenarios

### Step 4: stress-aggregation [depends_on: scenario-crash-simulator, interest-rate-shock]
Aggregates stress-test drawdowns into a compliance card.
Expected: stress-metrics-scorecard

