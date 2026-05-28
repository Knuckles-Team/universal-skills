---
name: service-observability-provisioner
description: >
  Service Observability Provisioner atomic skill. Integrates new container log targets
  with Promtail and registers dynamic metrics scraping endpoints with Prometheus.
domain: infrastructure
tags:
  - observability
  - prometheus
  - grafana
  - promtail
  - logging
  - monitoring
requires:
  - systems-manager-mcp
  - portainer-mcp
---

# Service Observability Provisioner Skill

Stateless atomic operation to register and wire newly deployed services into the primary LGTM (Loki, Grafana, Temp, Prometheus) observability stack.

## Prerequisites

- `systems-manager-mcp` — for direct reading and editing of target collector configs (e.g. Promtail, Prometheus scrape targets).
- `portainer-mcp` — for validating container configurations, environment labels, and network ports.

## Steps

### Step 1: Link Promtail Logging Path
Configure log capture for the target application:
- Verify container-label structure or direct host mapping for container logs (typically `/var/lib/docker/containers/<id>/*.log`).
- Add the log config block to Promtail's scrape configuration:
  ```yaml
  - job_name: <service-name>-logs
    static_configs:
      - targets: [localhost]
        labels:
          job: <service-name>
          __path__: /var/lib/docker/containers/*/<id>*.log
  ```
- Trigger reload or restart of the Promtail collector container.

### Step 2: Register Prometheus Metrics Scraper
Set up metrics discovery:
- Add a new static or dynamic scraper job to `/home/apps/prometheus/prometheus.yml`:
  ```yaml
  - job_name: '<service-name>'
    static_configs:
      - targets: ['<container-name>:<internal-metrics-port>']
  ```
- Hot-reload the Prometheus configuration via REST endpoint POST `/sys/reload` or container restart.

### Step 3: Verify Telemetry Flows
Confirm log shipping and metric collection:
- Verify logs are queryable in Grafana Loki.
- Confirm metrics show as `UP` in Prometheus target status.
