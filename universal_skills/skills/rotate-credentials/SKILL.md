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
  version: '1.6.2'
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

## Steps

1. Confirm the request carries a `rotation_profile_ref` that resolves to inventory, provider, account, secret and policy references (a `rotation_profile_ref` of this shape is required). Verify that every reference resolves and that none exposes a secret value, otherwise reject the request.
2. Ask the configured provider for a value-free dry-run (target count, credential classes, policy digests, rollback readiness) using only the `rotation_profile_ref` as input. Verify that the response contains no credential values or hostnames and that it reports rollback as ready.
3. Obtain explicit approval for the exact `dry-run digest`. Verify that the approval reference names that digest before any rotation call.
4. Invoke the provider's credential-rotation capability with only the `rotation_profile_ref` and the approval reference. Verify that each target was rotated one at a time and confirmed by the provider's separate check, with the previous secret version kept until that check passes.
5. Return the retained output listed under `## Retained output`. Verify that it holds only counts, opaque target references, secret-version references, digests, timestamps and an audit reference.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The `rotation_profile_ref` does not resolve | The AgentConfig profile is missing or misnamed | Stop, ask the operator to fix the profile, and do not accept raw credentials or hostnames as a substitute |
| Provider lacks the credential-rotation capability | The configured provider profile does not support the account or BMC class | Stop and report the missing capability, and do not improvise shell commands or use `scripts/rotate-credentials.sh` |
| A target verification is indeterminate | The separate provider check timed out or returned an unclear state | Stop the campaign, keep the previous secret version, and report the opaque target reference as failed so the provider can roll back |
| Dry-run digest differs at approval time | The inventory or policy changed after the dry-run | Discard the approval, request a new dry-run, and approve the new digest |

## Retained output

Return aggregate success/partial/failure counts, opaque target references for any
failures, secret-version references, provider and policy digests, timestamps, and
an audit reference. Never retain account names, hostnames, addresses, local paths,
credential values, command output, or operator identity.
