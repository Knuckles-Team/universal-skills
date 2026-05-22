---
name: tunnel_and_network_audit
description: Audit active SSH tunnels and network connectivity alongside system network interface status.
domain: infrastructure
tags: ['tunnels', 'network', 'security', 'audit']
requires: ['tunnel-manager', 'systems-manager']
---

# tunnel_and_network_audit Workflow

Audit active SSH tunnels and network connectivity alongside system network interface status.

### Step 0: tunnel-manager
List all active tunnels from the inventory
Expected: tunnel

### Step 1: systems-manager
Show network interface stats and active connections
Expected: network, interface

### Step 2: systems-manager
Get the system's firewall rules summary
Expected: firewall, rule
Depends On: Step 0, Step 1
