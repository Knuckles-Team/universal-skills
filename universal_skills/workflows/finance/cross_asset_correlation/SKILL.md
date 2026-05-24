---
name: cross_asset_correlation
description: Collects multi-ticker price data, constructs rolling correlation matrices, flags eigen anomalies, and adjusts portfolio scale limits.
domain: finance
tags: [correlation, cross-asset, matrix, risk]
---
# Cross Asset Correlation Workflow

This workflow coordinates multi-agent parallel executions of Collects multi-ticker price data, constructs rolling correlation matrices, flags eigen anomalies, and adjusts portfolio scale limits.

### Step 1: multi-ticker-collector [depends_on: none]
Collects price feeds for spot equities, commodities, and currencies concurrently.
Expected: multi-asset-historical-prices

### Step 2: correlation-matrix-fitter [depends_on: multi-ticker-collector]
Computes standard rolling correlation matrices and eigenvalues.
Expected: rolling-correlation-matrices

### Step 3: eigen-anomaly-detector [depends_on: correlation-matrix-fitter]
Flags breakdowns in historical sector correlations.
Expected: eigenvalue-breakdown-signals

### Step 4: risk-exposure-adjuster [depends_on: eigen-anomaly-detector]
Updates portfolio limit scales to mitigate systemic contagion.
Expected: adjusted-portfolio-limits

