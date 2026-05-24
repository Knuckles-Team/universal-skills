---
name: options_volatility_surface
description: Fetches multi-expiry options chain price metrics, fits implied volatility surface curves, and identifies skew arbitrage.
domain: finance
tags: [options, volatility, iv, skew]
---
# Options Volatility Surface Workflow

This workflow coordinates multi-agent parallel executions of Fetches multi-expiry options chain price metrics, fits implied volatility surface curves, and identifies skew arbitrage.

### Step 1: options-feed-collector [depends_on: none]
Fetches option chain price logs and strike parameters across multiple expiries.
Expected: raw-options-chain-feeds

### Step 2: iv-surface-fitter [depends_on: options-feed-collector]
Fits an implied volatility surface and calculates volatility smiles.
Expected: implied-volatility-surface

### Step 3: anomaly-detector [depends_on: iv-surface-fitter]
Identifies mispriced options contracts and volatility skew anomalies.
Expected: volatility-skew-anomalies

### Step 4: arbitrage-executor [depends_on: anomaly-detector]
Proposes volatility trade executions to profit from the spreads.
Expected: options-arbitrage-orders

