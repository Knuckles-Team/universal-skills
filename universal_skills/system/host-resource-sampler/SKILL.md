---
name: host-resource-sampler
skill_type: skill
description: >
  System resource sampling atomic skill. Gathers CPU, memory, disk, and load
  average utilization metrics across multiple remote hosts via SSH.
domain: system
license: MIT
tags: [metrics, host, monitoring, system, telemetry]
metadata:
  version: '1.1.0'
  author: Genius
requires:
  - systems-manager-mcp
  - tunnel-manager-mcp
---

# Host Resource Sampler Skill

Stateless atomic operation to establish SSH connections or invoke system utility calls across inventory hosts, execute diagnostic metrics sweeps, parse utilization outputs (CPU core loads, memory allocation, storage disk capacities, process queue sizes), and output a standardized telemetry JSON structure indicating current server constraints.

## Prerequisites

- `systems-manager-mcp` — for retrieving OS statistics, executing diagnostic shell probes, and sampling process metrics.
- `tunnel-manager-mcp` — for executing commands concurrently across remote nodes.

## Steps

### Step 1: execute_resource_queries
Coordinate concurrent telemetry sweeps across target hosts using secure command pipelines:
- Construct diagnostic sampling commands:
  - CPU & Load Average: `top -bn1 | grep "Cpu(s)"` or `cat /proc/loadavg`
  - Memory: `free -m` or `vmstat 1 2`
  - Disk Space & I/O: `df -h` and `iostat -d 1 2` (if available)
- Invoke remote sweeps:
  - Dispatch commands concurrently using `tunnel-manager-mcp` (e.g. `run_command` across the target cluster group or single inventory alias).
  - Capture standard stdout metrics logs and stderr messages.
- Output parameters:
  - `sampling_results`: Key-value map of host aliases to their raw command output logs.

### Step 2: parse_utilization_metrics [depends_on: execute_resource_queries]
Extract numerical utilization ratios and parse raw streams using robust pattern matches:
- Parse CPU usage:
  - Extract idle percentage (`id`) and calculate active CPU load percentage (`100 - idle`).
  - Extract 1-minute, 5-minute, and 15-minute load averages.
- Parse Memory metrics:
  - Extract total, used, free, and buffered/cached memory sizes in megabytes.
  - Calculate memory usage percentage: `(used / total) * 100`.
- Parse Disk partition utilization:
  - Map active mount points (specifically root `/` and primary data volumes).
  - Extract percentage used and absolute gigabytes remaining.
- Output parameters:
  - `host_metrics`: Detailed mapping of host metrics including `{ cpu_pct: Float, load_avg: List, mem_pct: Float, disk_pct: Float }`.

### Step 3: compile_telemetry_report [depends_on: parse_utilization_metrics]
Synthesize the metrics scorecard and execute warning rules for system limits:
- Identify high-utilization alerts:
  - Mark hosts exceeding defined limits (e.g. CPU > 90%, Memory > 92%, Disk Space > 88%).
- Format output payloads:
  - Standardize JSON object of the sweep status.
  - Build a clean markdown utilization dashboard displaying host columns, system bars, and highlight symbols next to any alert-flagged nodes.
- Output parameters:
  - `status`: "SUCCESS" or "FAILED"
  - `payload`: Standardized JSON representation of the host utilization.
  - `summary_markdown`: Markdown visualization of the server metrics dashboard.
