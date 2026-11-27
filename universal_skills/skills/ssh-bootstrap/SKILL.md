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
  version: '1.7.0'
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

## Steps

1. Confirm the five AgentConfig references resolve (`inventory_ref`, `remote_profile_ref`, `key_profile_ref`, optional `target_selector_ref` and `concurrency_policy_ref`). Verify that tunnel-manager returns a privacy-safe connectivity summary for them, and stop if any reference is unresolved.
2. Present the summary to the owner with target count, current trust count, scope, key-policy digest and host-key-policy digest. Verify that explicit approval was given before any key or `authorized_keys` change.
3. Run `mcp_tm_inventory` with `action="mesh_bootstrap"` through the resolved profiles. Verify that the provider reports every approved source-to-target trust edge as authenticated non-interactively.
4. Record only the retained output (counts, status, digests, timestamps and an opaque run reference) and scan it with `grep -nEi 'ssh-ed25519|password|@' <retained-output>`. Verify that nothing retained contains a hostname, address, username, path or key material.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Reference cannot be resolved | A named AgentConfig reference is missing or misspelled | Ask the owner to define it in AgentConfig and rerun step 1; never pass raw endpoints or credentials |
| Result is partial | Some trust edges failed authentication | Report status as partial with the opaque failed references, fix the host-key or key policy, and rerun `mesh_bootstrap` for those targets only |
| Provider asks for a password | Host does not yet trust the key and no governed credential exists | Stop and obtain a governed secret-provider reference; do not fall back to `sshpass` or a password file |
| Host-key verification fails | Changed or unknown host key under a strict policy | Have the owner confirm the new key out of band and update the host-key policy, rather than disabling verification |

## Retained output

Return only target and trust-edge counts, success/partial/failure status, key and
policy digests, timestamps, and an opaque run reference. Never retain hostnames,
addresses, usernames, local paths, public-key comments, key material, passwords,
or raw command output.
