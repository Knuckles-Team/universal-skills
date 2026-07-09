---
name: automated-credential-rotation
domain: infrastructure
skill_type: skill
description: >-
  Holistically and safely rotate fleet secrets (GitHub/GitLab PATs, Keycloak
  OIDC client secrets, database passwords, LLM/API keys, OTEL/Langfuse keys,
  registry creds) with OpenBao as the source of truth. Rotates at the provider,
  writes the new value to OpenBao, propagates to consumers (Portainer stack env,
  Keycloak, agent-utilities config), verifies, and revokes the old — never
  echoing a secret value. Dry-run first; supports a 6-month rotation policy. Use
  when asked to rotate credentials/secrets/tokens/keys, set up periodic rotation,
  respond to a leaked credential, or audit secret age. Ties into
  agent-utilities-deployment and agent-os-genesis. Do NOT use for OS/SSH login or
  BMC passwords (use rotate-credentials) or one-off vault writes (use
  secret-vault-manager).
license: MIT
tags: [infra, security, credentials, secrets, rotation, openbao, keycloak, portainer, policy]
metadata:
  version: '1.0.2'
  author: Genius
---

# Automated Credential Rotation

## Overview

End-to-end, **safe** rotation of application secrets across the fleet, with
**OpenBao as the single source of truth**. Every rotation follows the same atomic
flow and **never prints a secret value** — outputs carry names, versions, and
status only. Default mode is **dry-run**: produce a plan, review it, then execute.

This skill *orchestrates existing tools* — it doesn't reinvent them:
- **OpenBao** (`openbao_mcp_kv` / `openbao_mcp_logical`) — store of record.
- **Portainer** (`port__stack` `update_stack`) — inject rotated env into stacks + restart.
- **Keycloak** (`keycloak-agent`) — OIDC client-secret regeneration.
- **GitLab** (`gitlab-api`) / **GitHub** (`gith__*`) — provider PAT/token rotation + CI vars.
- **rotate-credentials** skill — OS/SSH + BMC passwords (this skill delegates those).
- `scripts/rotation_lib.py` — the deterministic safety layer (generate / redact /
  plan / audit), stdlib-only and value-free by construction.

## Safety rules (non-negotiable)

1. **Never echo a value.** Route any text that might contain a secret through
   `rotation_lib.redact` (or `safe_dumps`). Tool results that return values
   (e.g. Portainer `get_stack_by_name` returns env values) must be summarized,
   not pasted. Generate secrets with `rotation_lib.generate_secret`.
2. **Dry-run first.** Build and present the plan; only execute after approval.
3. **Validate before propagate.** Confirm the new value works at the provider
   and the OpenBao version incremented before touching any consumer.
4. **Keep the old until verified.** OpenBao KV2 retains the prior version; only
   revoke the old credential at the provider after consumers verify.
5. **Per-consumer atomicity.** One consumer failing must not abort the rest;
   record partial status.

## Inputs

- **catalog**: a list of secrets to manage (see `references/catalog.example.json`).
  Each entry: `{name, type, provider, bao_path, consumers[], cadence_days, verify}`.
- **scope**: a secret name, a type, or `all`. **mode**: `dry-run` (default) | `execute`.

## Workflow (per secret — same flow every time)

1. **Plan** — `python scripts/rotation_lib.py plan --catalog catalog.json` renders a
   value-free, ordered plan (rotate → write → validate → propagate → verify → revoke).
   Present it. Stop here in dry-run.
2. **Rotate at provider** (execute mode):
   - GitHub PAT: create a new fine-scoped token (`gith__*` / GitHub settings), keep the id of the old.
   - GitLab PAT: `gitlab-api` create personal/project access token; note the old id.
   - Keycloak client: regenerate the client secret (`keycloak-agent`).
   - DB password: generate with `rotation_lib.generate_secret --kind password`; `ALTER USER`.
   - Generic API/LLM/OTEL key: rotate in the provider console/API.
3. **Write to OpenBao** — `openbao_mcp_kv action=kv2_put mount_path=secret
   secret_path=<bao_path> params_json={"data":{"value":"<new>","rotated_at":"<ts>"}}`.
   Then `kv2_get` and assert the returned version is greater than before.
4. **Propagate to consumers** (from the catalog):
   - **Portainer stack env**: `port__stack action=update_stack` with the new env.
     ⚠️ This requires re-sending the stack env (which includes other secrets) — do it
     via the tool, never paste the values into the conversation; pull current env from
     OpenBao, not from chat. (If the stack reads the secret from OpenBao at boot, just
     restart the service instead — no value passes through.)
   - **agent-utilities config**: rewrite `vault://` refs via `setup-config`; restart graph-os.
   - **CI variables**: `gitlab-api` update CI/CD variable; GitHub Actions secret via API.
5. **Verify** — hit the consumer's auth path (provider whoami, DB connect, MCP `/health`).
6. **Revoke old** — delete/expire the previous token at the provider once verified.
7. **Audit** — append a `rotation_lib.audit_record(...)` (names/versions/status only) to
   the run report. Summarize: rotated N, partial M, failed K.

## Policy & scheduling (6-month baseline)

Per-type cadence lives in the catalog (`cadence_days`, default 182). Drive periodic
runs with the `schedule` skill / a cron routine, e.g. monthly at an off-peak minute,
filtered to secrets whose age exceeds `cadence_days`. Always run `mode=dry-run` on a
schedule and require approval (or a signed window) before `execute` for high-stakes
secrets (Keycloak, DB, registry).

## Integration

- **agent-utilities-deployment**: after secrets are provisioned (its Step 3 `vault://`
  resolution), this skill is the rotation counterpart — same catalog, same OpenBao paths.
- **agent-os-genesis**: register this skill as the recurring rotation step after SSO
  wiring; genesis provisions the initial secrets, this rotates them on policy.

## Verification (of this skill)

- `python scripts/rotation_lib.py gen --kind password` → a strong value (used once).
- `echo 'GITHUB_TOKEN=ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' | python scripts/rotation_lib.py redact`  <!-- # sanitizer:ignore — illustrative non-secret demo token (all-A's), not a real PAT -->
  → the value is `***REDACTED***`.
- `python scripts/rotation_lib.py plan --catalog references/catalog.example.json` → a
  value-free plan. Confirm no secret material appears anywhere in output.

## Related
- `rotate-credentials` — OS/SSH + BMC passwords (delegate those here).
- `secret-vault-manager` — OpenBao unseal/init + one-off KV writes.
- `keycloak-client-onboarder` — initial OIDC client provisioning.
