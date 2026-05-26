---
name: swarm-mesh-provisioner
description: >
  Swarm Mesh Provisioner atomic skill. Initializes Docker Swarm Mode,
  manages manager/worker nodes join processes, and provisions global Swarm Overlay networks using container-manager-mcp.
domain: infrastructure
tags:
  - swarm
  - docker
  - overlay-net
  - cluster
requires:
  - container-manager-mcp
  - tunnel-manager-mcp
---

# Swarm Mesh Provisioner Skill

Stateless atomic operation to establish multi-node container orchestration clusters and secure virtual networks.

## Prerequisites

- `container-manager-mcp` — for executing Swarm init, join, network, and node operations.
- `tunnel-manager-mcp` — for running command execution on worker nodes.

## Steps

### Step 1: Initialize Swarm Manager
On the target Manager node, verify Swarm status. If inactive:
- Run `docker swarm init` specifying advertise address.
- Retrieve manager and worker join tokens.

### Step 2: Join Swarm Workers
For each designated worker node listed in the inventory:
- Verify remote Docker engine state.
- Join the Swarm cluster using the worker join token.
- Validate active cluster membership.

### Step 3: Provision Global Overlay Network
Create a secure, encrypted overlay network (e.g., `overlay-net`) to bridge containers across different hardware hosts:
- Ensure the network is created with `--attachable` to support dynamic containers.
- Check MTU and driver settings.

### Step 4: Verify Cluster State
Confirm that all node statuses read `Ready` and state shows `Active` on the Swarm manager.
