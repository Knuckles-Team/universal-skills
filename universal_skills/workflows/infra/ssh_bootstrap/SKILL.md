---
name: ssh_bootstrap
description: Interactive SSH key bootstrap for new infrastructure hosts. Checks existing connectivity, generates RSA keys if missing, and distributes them via tunnel-manager to establish passwordless SSH access for future discovery scans.
domain: infrastructure
tags: ['ssh', 'bootstrap', 'keys', 'onboarding', 'security']
requires: ['tunnel-manager-mcp', 'systems-manager-mcp']
---

# ssh_bootstrap Workflow

Interactive SSH key bootstrap for new infrastructure hosts. Checks existing connectivity, generates RSA keys if missing, and distributes them via tunnel-manager to establish passwordless SSH access for future discovery scans.

### Step 0: tunnel-manager-mcp
List all hosts from the inventory file and check current SSH connectivity status
Expected: host, inventory, status

### Step 1: systems-manager-mcp
Check if SSH keys exist at ~/.ssh/id_rsa. If not, generate a new RSA key pair
Expected: ssh, key, generate
Depends On: Step 0

### Step 2: tunnel-manager-mcp
For each host that failed connectivity, set up passwordless SSH using the generated key
Expected: ssh, passwordless, setup
Depends On: Step 1

### Step 3: tunnel-manager-mcp
Verify connectivity to all hosts after key distribution
Expected: verify, connectivity
Depends On: Step 2
