---
name: ssh-bootstrap
domain: infrastructure
skill_type: skill
description: >
  Interactive SSH key bootstrap for new infrastructure hosts. Checks existing
  connectivity, generates RSA keys if missing, and distributes them via
  tunnel-manager-mcp to establish passwordless SSH access. Default behavior
  is full-mesh: every inventory host can reach every other host without
  passwords. Use when onboarding new servers, setting up a homelab, or
  preparing machines for infrastructure discovery. Triggers on "setup ssh",
  "bootstrap keys", "onboard host", "passwordless ssh", "prepare machines".
  Do NOT use for ongoing SSH session management — use tunnel-manager directly.
metadata:
  version: '1.2.0'
---

# SSH Bootstrap Skill

Interactive SSH key generation and full-mesh distribution for infrastructure onboarding.

## Prerequisites

- `tunnel-manager-mcp` — for inventory access and SSH key distribution
- `systems-manager-mcp` — for local key generation and host probing
- `~/.config/agent-utilities/inventory.yaml` — canonical host inventory

## Default Behavior: Full-Mesh Passwordless SSH

By default, this skill establishes **full-mesh** connectivity: every inventory
host can SSH to every other inventory host without passwords using RSA keys.
This means:

1. The local machine gets a key pair and distributes to all hosts
2. Each remote host gets a key pair generated and distributed to all other hosts
3. Result: any host → any host SSH without password prompts

> **IMPORTANT**: Always confirm with the user before proceeding with key
> generation and distribution. Prompt: "Set up full-mesh passwordless SSH
> across all inventory hosts? This will generate RSA keys on each machine
> and distribute them to all others. Proceed? (y/n)"

## Inventory Scope

Only **real hardware** hosts belong in `inventory.yaml`. Do NOT include:
- **Macvlan containers** (e.g., `technitium-dns` at `10.0.0.199`, `home-assistant`)
  — these have dedicated IPs but no SSH daemon. They are tracked as `Container`
  nodes in the KG with `RUNS_ON` edges to their physical host.
- **Regular containers** — tracked via portainer/container-manager MCP tools.

## Workflow

### Step 1: Inventory Check

Read the inventory and check SSH connectivity status:

```
Use tunnel-manager-mcp → list all registered hosts
For each host, attempt SSH connection (BatchMode) to verify access
Report: reachable vs unreachable hosts
```

### Step 2: Local Key Generation (if needed)

Check if the local machine has SSH keys:

```
Check if ~/.ssh/id_rsa exists
If missing:
  - PROMPT THE USER: "No SSH key found. Generate a new RSA-4096 key pair? (y/n)"
  - If approved: ssh-keygen -t rsa -b 4096 -N "" -C "genius@agent-os"
```

### Step 3: Distribute Local Key to All Hosts

For each unreachable host:

```
PROMPT THE USER: "Distribute SSH key to all inventory hosts? (y/n)"
If approved:
  - Use password from user-provided file OR prompt for password
  - Use tunnel-manager-mcp → setup_passwordless for each host
  - Alternatively: sshpass -f <password_file> ssh-copy-id -i ~/.ssh/id_rsa.pub user@host
```

### Step 4: Full-Mesh Key Distribution (Default)

Instead of performing the complex N×N key generation and distribution loop manually, **always use the native `mcp_tm_inventory` tool with the `mesh_bootstrap` action**. This performs a highly optimized, fully concurrent, cross-platform (Linux/Windows) key generation, public key collection, full-mesh authorized_keys distribution, and known_hosts keyscan setup in a single step.

**Executing with `mcp_tm_inventory`**:
- **action**: `"mesh_bootstrap"`
- **inventory**: optional path to the `inventory.yaml` (defaults to XDG config if omitted)
- **key**: optional path to the local SSH private key
- **key_type**: `"ed25519"` or `"rsa"` (defaults to `"ed25519"`)
- **group**: optional target inventory group (e.g. `"homelab"`)
- **parallel**: `true` (enables fully parallel orchestration across all hosts)
- **max_threads**: optional maximum concurrent workers

This single-step operation is completely robust and auto-detects target host operating systems (Linux/Windows) to run appropriate path-handling, keygen, and environment setup commands.

#### Manual/Fallback Distribution Loop (Only if tool is unavailable):

If for any reason the native tool cannot be executed, fall back to the manual process:
```
For each host A in inventory:
  1. SSH into host A
  2. Check if SSH key exists (~/.ssh/id_ed25519 or %USERPROFILE%\.ssh\id_ed25519); if not, generate one
  3. Read host A's public key
  4. For each other host B in inventory:
     - Append A's public key to B's ~/.ssh/authorized_keys (or %USERPROFILE%\.ssh\authorized_keys)
     - Run ssh-keyscan on host A for host B to populate known_hosts
  5. Also add A's key to the local machine's authorized_keys and update local known_hosts

Result: Full N×N mesh connectivity
```

### Step 5: Verification

Re-check connectivity across the full mesh:

```
From local: SSH to each host (BatchMode) → verify
From each host: SSH to each other host → verify
Report final mesh status
```

### Step 6: Hardware Sweep (Optional)

If all hosts are now reachable, offer to run a hardware sweep:

```
PROMPT THE USER: "All hosts reachable. Run hardware sweep to collect
OS and system info for the Knowledge Graph? (y/n)"

If approved, run the hardware-sweep workflow from catalog.yaml
```

## Password Handling

When distributing keys to unreachable hosts, a password is needed once.
Supported methods (in priority order):
1. **Password file**: User provides path to a plaintext file with the password
2. **Interactive prompt**: Ask user to enter password
3. **tunnel-manager-mcp**: Use `setup_passwordless` with `password` parameter

> **SECURITY**: Never log, store, or display passwords. Password files should
> be deleted after use.

## Catalog Workflow

This skill maps to the `ssh-bootstrap-workflow` workflow in `catalog.yaml`:

```yaml
- name: ssh-bootstrap-workflow
  domain: infrastructure
  requires: [tunnel-manager-mcp, systems-manager-mcp]
  steps:
    1. List hosts and check connectivity
    2. Check/generate SSH keys (local)
    3. Distribute local key to all hosts
    4. Generate keys on remotes + full-mesh distribution
    5. Verify full mesh connectivity
```

## Integration with Infrastructure Orchestrator

The `infrastructure-orchestrator` skill invokes this skill as a prerequisite
before running discovery. If hosts are unreachable during
`full-infrastructure-discovery`, suggest running `ssh-bootstrap-workflow` first.

## KG Node Updates

After successful bootstrap, update the KG:
- `HardwareNode.status` → `reachable`
- `HardwareNode.ssh_key_fingerprint` → key fingerprint
- `HardwareNode.last_connectivity_check` → ISO timestamp
