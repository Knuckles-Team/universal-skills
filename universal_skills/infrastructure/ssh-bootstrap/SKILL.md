---
name: ssh-bootstrap
domain: infrastructure
skill_type: skill
description: >-
  Establish governed passwordless SSH trust for hosts selected by an
  AgentConfig inventory and remote-access profile. Use when onboarding servers,
  repairing missing SSH trust, or preparing managed hosts for infrastructure
  discovery. Do not use for ongoing remote command execution, application
  credentials, or hosts outside the configured inventory.
requires:
  - tunnel-manager-mcp
metadata:
  version: '1.2.1'
---

# SSH bootstrap

Run the tunnel-manager inventory provider's native `mesh_bootstrap` operation.
This skill defines one capability: establish and verify SSH trust for the
deployment-owned target set. Keep host topology, account names, addresses, key
locations, passwords, and platform exceptions outside the skill.

## Runtime contract

Require these named AgentConfig references:

- `inventory_ref`: managed hosts and deployment-owned groups;
- `remote_profile_ref`: transport, account, privilege, host-key, and timeout policy;
- `key_profile_ref`: key algorithm, rotation policy, and secret-provider reference;
- optional `target_selector_ref`: the approved subset of inventory hosts;
- optional `concurrency_policy_ref`: bounded worker limits for discovery and setup.

Reject unresolved references. Do not accept raw endpoints, usernames, passwords,
private-key paths, or inventory file paths in the skill payload. The AgentConfig
resolver may supply those values directly to the configured provider at runtime,
but they must not enter prompts, logs, graph properties, or retained output.

## Operation

Before mutation, ask tunnel-manager to resolve the references and return a
privacy-safe connectivity summary. Present the target count, current trust count,
requested scope, key-policy digest, and host-key-policy digest. Require explicit
approval when any key or `authorized_keys` state will change.

Invoke `mcp_tm_inventory` with `action="mesh_bootstrap"` through the resolved
profiles. Let the provider choose platform-specific key locations and commands.
Use Ed25519 unless the referenced policy requires another supported algorithm.
Scope distribution exactly as the inventory policy specifies; full mesh is not an
implicit default. Never fall back to `sshpass`, a plaintext password file, inline
shell loops, or an unverified host-key policy.

Treat the operation as unsuccessful unless the provider verifies every approved
source-to-target trust edge with non-interactive authentication. A partial result
must identify failed opaque host references without exposing their addresses or
accounts, and must not be described as complete.

## Retained output

Return only target and trust-edge counts, success/partial/failure status, key and
policy digests, timestamps, and an opaque run reference. Never retain hostnames,
addresses, usernames, local paths, public-key comments, key material, passwords,
or raw command output.
