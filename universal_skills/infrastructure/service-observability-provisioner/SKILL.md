---
name: service-observability-provisioner
skill_type: skill
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
metadata:
  version: '1.0.2'
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

### Step 2b: Register Service Dashboard
Surface the new service's metrics in Grafana (datasources + a dashboard provider are already
provisioned-as-code under `services/lgtm/grafana/provisioning/`; the Prometheus datasource
`uid` is `prometheus`):
- **MCP / fleet services** need **no new dashboard** — the templated **MCP Per-Service**
  dashboard (`$stack` variable, `label_values(up{job="mcp-fleet"}, stack)`) and the
  **MCP Fleet Overview** pick it up automatically once it scrapes. Just confirm the new
  service appears in the `$stack` picker and the **Container Resources** dashboard (it groups
  by `container_label_com_docker_swarm_service_name`, kept by the cAdvisor label whitelist).
- **Bespoke platform services** (own `/metrics`, e.g. keycloak/immich/langfuse): add a panel
  set by **extending the generator** `agent-utilities/scripts/gen_grafana_dashboards.py` (a new
  `*()` builder + an entry in `main()`), then re-run it — dashboards are generated as code, so a
  hand-edited JSON in `dashboards/json/` is clobbered on the next run. Reference panels as:
  ```json
  { "datasource": { "type": "prometheus", "uid": "prometheus" },
    "targets": [ { "expr": "<your_service_metric>" } ] }
  ```
- The dashboard provider auto-loads new JSON from `dashboards/json/` within
  `updateIntervalSeconds` (30s) — no Grafana restart needed.

### Step 3: Verify Telemetry Flows
Confirm log shipping and metric collection:
- Verify logs are queryable in Grafana Loki.
- Confirm metrics show as `UP` in Prometheus target status.
- Confirm the service's panels render in Grafana (its `$stack` row in MCP Per-Service, or its
  bespoke dashboard) with live data.
