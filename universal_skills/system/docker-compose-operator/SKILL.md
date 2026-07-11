---
name: docker-compose-operator
skill_type: skill
description: >
  Universal Docker Compose and Swarm operation and deployment atomic skill.
  Compiles environment templates, triggers service deploys, and monitors operational health.
domain: system
license: MIT
tags: [docker, compose, swarm, deployment, system]
metadata:
  version: '1.2.0'
  author: Genius
requires:
  - container-manager-mcp
---

# Docker Compose Operator Skill

Stateless atomic operation to compile template compose definitions, resolve active environment parameter overlays, deploy/restart Docker containers or Swarm stacks safely, and monitor container execution logs to verify operational health.

## Prerequisites

- `container-manager-mcp` — for initiating compose actions (`up`, `down`, `ps`, `logs`), deploying service stacks, and monitoring process readiness.

## Steps

### Step 1: compile_compose_manifest
Assemble the targeted deployment specifications and validate syntax and overrides:
- Locate the reference compose YAML file (e.g. `docker-compose.yml` or `stack.yml`) and its corresponding `.env` or configuration parameters.
- Substitute template variables, environment configuration keys, and host path references.
- Execute validation on the compiled compose syntax (e.g. verify YAML validity, check that image references are fully qualified, and check that required volume mounts exist on the host).
- Output parameters:
  - `manifest_valid`: Boolean indicating successful compilation.
  - `resolved_manifest_path`: Absolute path to the validated temporary compose file.

### Step 2: execute_compose_deployment [depends_on: compile_compose_manifest]
Execute deployment operations with safety checks:
- Trigger container launch:
  - Invoke `up` or stack `deploy` operations via `container-manager-mcp` (e.g., using `cm_compose_operations`).
  - Pass the compiled configuration file and specify proper namespace/stack definitions.
- Coordinate dependencies and rolling replacements:
  - Verify if pre-requisite backing databases or network subnets are operational before launching core app containers.
  - Enforce graceful termination timeouts for old container replicas to prevent socket drops.
- Output parameters:
  - `deployment_exit_code`: Int process return code.
  - `deployment_raw_output`: String command outputs.

### Step 3: verify_operational_health [depends_on: execute_compose_deployment]
Perform granular verification of the active containers to ensure readiness and stability:
- Poll container states:
  - Wait for containers to exit boot phases, querying runtime statuses (`running`, `healthy`, `restarting`).
- Log inspection and error parsing:
  - Retrieve and parse container stdout/stderr logs (e.g. using `get_container_logs` action).
  - Scan for common startup exceptions (e.g., `ConnectionRefusedError`, `Database error`, `Exception`).
- readiness probes:
  - If web ports or health check endpoints are mapped, test their accessibility (expecting standard `200 OK` or valid TCP socket connections).
- Output parameters:
  - `status`: "SUCCESS" or "FAILED"
  - `active_containers`: List of running service instances with their states.
  - `health_log_summary`: Summary of any anomalies or startup errors discovered.
