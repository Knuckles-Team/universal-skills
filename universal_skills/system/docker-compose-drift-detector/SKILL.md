---
name: docker-compose-drift-detector
skill_type: skill
description: >
  Docker Compose and Swarm configuration drift detection atomic skill.
  Compares running state against git configuration.
domain: system
license: MIT
tags: [docker, swarm, infrastructure, drift]
metadata:
  version: '1.0.2'
  author: Genius
requires:
  - container-manager-mcp
---

# Docker Compose Drift Detector Skill

Stateless atomic operation to query Docker containers/Swarm services, retrieve active running configurations, parse reference Compose/YAML template repositories, and perform automated drift detection of images, environments, and mounts.

## Prerequisites

- `container-manager-mcp` — for inspecting active containers, query image manifests, list service definitions, and inspect active cluster configurations.

## Steps

### Step 1: retrieve_active_topology
Fetch real-time execution telemetry and configuration parameters from running containers:
- Query active container landscape:
  - Fetch list of running containers or Swarm services via `container-manager-mcp` (e.g., using `list_containers` action).
  - Filter target containers by namespace, stack name, or specific project identifier.
- Inspect detailed configuration properties:
  - Query specific properties of each targeted container or service (image name, image tag, exact registry digest hash, active environment variables, volume mount mappings, network attachments, and replica counts).
- Output parameters:
  - `active_containers`: Mapping of container names to their active running state configuration objects.

### Step 2: diff_configurations [depends_on: retrieve_active_topology]
Locate and parse target Compose template files and execute differential comparison analysis:
- Locate configuration templates:
  - Scan repository folders or target workspace paths for compose files (e.g., `docker-compose.yml`, `caddy-compose.yml`, stack templates).
- Parse and resolve templates:
  - Read target reference compose files.
  - Substitute environment variables and `.env` properties to resolve template values as they would be generated in deployment.
- Granular differential review:
  - Perform element-by-element comparison between the running container configuration and the resolved reference compose file.
  - Compare target fields:
    - **Image/Tag**: Verify if the running tag/digest matches the reference specification.
    - **Environment Overrides**: Compare key-value pairs of active environment variables.
    - **Mount Configuration**: Ensure host paths and container mount points are synchronized.
    - **Replicas/Scale**: Check if active counts match template directives.
- Output parameters:
  - `drift_detected`: Boolean indicating if any differences were discovered.
  - `drift_matrix`: Object mapping each mismatched attribute to its `template` and `running` value.

### Step 3: report_drift_status [depends_on: diff_configurations]
Categorize drift severity and format telemetry reports:
- Classify drift types:
  - `IMAGE_DRIFT`: Indicates container is running an out-of-date image or a different tag compared to the git repository.
  - `ENV_DRIFT`: Indicates missing or mismatched environment configuration keys.
  - `SCALE_DRIFT`: Indicates replica or service sizing mismatch.
- Compile summary payload:
  - Synthesize a comprehensive JSON and Markdown representation of the configuration differences.
- Output parameters:
  - `status`: "SUCCESS" or "FAILED"
  - `drift_summary`: Markdown summary of detected variations.
  - `severity`: String indicating action priority ("NONE", "LOW", "MEDIUM", "HIGH").
