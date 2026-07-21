---
name: rotate-credentials
domain: infrastructure
skill_type: skill
description: >-
  Rotate operating-system account or BMC credentials across an AgentConfig-managed
  host selection through governed remote and secret-provider profiles. Use for an
  approved fleet credential rotation, recovery-credential change, or BMC credential
  campaign. Do not use for SSH keys, application tokens, OIDC clients, or raw
  one-host password commands.
license: MIT
tags: [infra, security, credentials, password, bmc, fleet, rotation]
requires:
  - systems-manager-mcp
  - tunnel-manager-mcp
metadata:
  version: '1.2.1'
---

# Rotate host credentials

Perform one governed host-credential rotation campaign. Keep inventory details,
account identities, credentials, connection data, and provider-specific quirks in
deployment-owned AgentConfig profiles rather than this skill.

## Runtime contract

Require a `rotation_profile_ref` that resolves to:

- an inventory and target-selector reference;
- an authorized remote-execution provider profile;
- an account-selector reference;
- a secret generator/store reference;
- a verification and rollback policy;
- an optional BMC provider profile when BMC rotation is requested.

Reject unresolved references and profiles that expose secret values to the agent.
Do not accept credentials in chat, command arguments, environment variables,
plaintext files, or workflow output. Prefer unique credentials per target; a shared
recovery credential requires an explicit policy and approval recorded by the
provider.

## Operation

Ask the configured provider for a value-free dry-run containing the target count,
credential classes, provider capability status, policy digests, and rollback
readiness. Require explicit approval for the exact dry-run digest. Then invoke the
provider's credential-rotation capability using only the profile reference and
approval reference.

The provider must generate and transport secret material without returning it,
rotate one governed target at a time, verify the new credential through a separate
provider check, and retain the previous secret version until verification succeeds.
Stop on an indeterminate result. Do not improvise shell commands or fall back to a
bundled fleet script when the configured provider lacks the required capability.

## Retained output

Return aggregate success/partial/failure counts, opaque target references for any
failures, secret-version references, provider and policy digests, timestamps, and
an audit reference. Never retain account names, hostnames, addresses, local paths,
credential values, command output, or operator identity.
