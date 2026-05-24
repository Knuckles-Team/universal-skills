---
name: parameter_sweep_optimizer
description: Spawns 25 parallel parameter sweep configurations, extracts performance curves, plots response surfaces, and designates optimal param configs.
domain: finance
tags: [parameter-sweep, optimization, grid-search, visualization]
---
# Parameter Sweep Optimizer Workflow

This workflow coordinates multi-agent parallel executions of Spawns 25 parallel parameter sweep configurations, extracts performance curves, plots response surfaces, and designates optimal param configs.

### Step 1: grid-search-sweeper [depends_on: none]
Spawns 25 parallel parameter configuration models.
Expected: multi-parameter-backtest-records

### Step 2: metric-extractor [depends_on: grid-search-sweeper]
Extracts performance indicators and fit scores for each sweep node.
Expected: extracted-response-metrics

### Step 3: surface-plotter [depends_on: metric-extractor]
Generates a 3D parameter response surface map to identify stable basins.
Expected: volatility-response-surface-plot

### Step 4: config-selector [depends_on: surface-plotter]
Selects the parameters that minimize overfitting and registers them.
Expected: finalized-parameter-configs

