---
name: regime_detection_pipeline
description: Collects pricing indicators, extracts structural features, fits Hidden Markov Model classifiers, and adapts strategy params to structural shifts.
domain: finance
tags: [regime, hmm, volatility, classification]
---
# Regime Detection Pipeline Workflow

This workflow coordinates multi-agent parallel executions of Collects pricing indicators, extracts structural features, fits Hidden Markov Model classifiers, and adapts strategy params to structural shifts.

### Step 1: data-collector [depends_on: none]
Collects tick volumes, bid-ask spreads, and rolling volatilities.
Expected: market-regime-raw-data

### Step 2: feature-extractor [depends_on: data-collector]
Normalizes features and computes rolling volatility and trend indicators.
Expected: structured-regime-features

### Step 3: hmm-regime-fitter [depends_on: feature-extractor]
Fits a Hidden Markov Model (HMM) to classify market state.
Expected: hmm-state-classifications

### Step 4: regime-adapter [depends_on: hmm-regime-fitter]
Triggers strategy parameters modification based on the detected state.
Expected: adapted-parameters-configs

