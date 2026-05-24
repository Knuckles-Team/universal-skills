---
name: deploy_observability_stack
description: Deploys Prometheus, Grafana, and Loki in parallel and synthesizes dashboard integrations.
domain: infrastructure
tags: [prometheus, grafana, loki, docker, portainer, observability]
---
# Observability Stack Deployment

This workflow automates the deployment of Prometheus, Grafana, and Loki in parallel execution waves.

### Step 1: Prometheus Setup [depends_on: none]
Deploy the Prometheus container to scrape system metrics and container stats.
Expected: prometheus-running

### Step 2: Grafana Setup [depends_on: none]
Deploy the Grafana container and auto-register Prometheus and Loki data sources.
Expected: grafana-running

### Step 3: Loki Setup [depends_on: none]
Deploy the Loki logs aggregation server and configure sidecars.
Expected: loki-running

### Step 4: Observability Synth [depends_on: prometheus-setup, grafana-setup, loki-setup]
Configure default system health dashboards, alert rules, and verify final telemetry integration across all services.
Expected: system-integrated
