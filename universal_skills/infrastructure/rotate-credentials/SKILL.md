---
name: rotate-credentials
domain: infrastructure
skill_type: skill
description: >-
  Set one unified OS-account password across many hosts over SSH (and optionally the
  in-band iDRAC/BMC user), verifying each and reporting a per-host summary. Use when the
  user wants to rotate/unify/change login passwords across a fleet, set a shared recovery
  credential, onboard hosts to a common password, or rotate BMC passwords. Triggers:
  "rotate passwords", "unified password across hosts", "change my password everywhere",
  "set a shared console password". Do NOT use for SSH key distribution (use ssh-bootstrap),
  app/secret-store secrets (use secret-vault-manager), or single-host one-off passwd.
license: MIT
tags: [infra, security, credentials, password, ssh, ipmi, idrac, fleet, rotation]
metadata:
  version: '1.0.2'
  author: Genius
---

# Rotate Credentials

Set a single **unified password** for an OS account (default `genius`) across an entire
fleet over SSH, verify each host, and report OK/FAILED per host. Optionally rotate the
**in-band iDRAC/BMC** user-2 password in the same pass. Built to never abort on a bad
host — unreachable / sudo-prompting / crashing hosts are reported and skipped.

## When to use / not use
- **Use**: unify or rotate the login password across many hosts; set a shared recovery /
  console credential; rotate BMC user passwords; periodic credential rotation.
- **Skip**: SSH **key** setup (`ssh-bootstrap`); application/vault secrets
  (`secret-vault-manager`); a single host (`passwd` directly).

## Prerequisites
- `--ssh-user` (default `genius`) has **passwordless sudo** + SSH-key access on every host.
- `--idrac` additionally needs `ipmitool` + `/dev/ipmi0` on the target (in-band, no creds).

## Bundled resources
- `scripts/rotate-credentials.sh` — the rotation tool (SSH + `chpasswd` + `passwd -S`
  verify, optional `ipmitool` BMC rotation). Idempotent, fail-soft.
- `references/usage.md` — invocations, safety model, host quirks, recovery. **Read it**
  before a fleet-wide rotation or when a host reports FAILED.

## Procedure

### 1. Choose hosts + password
Hosts come from `--hosts "ip1 ip2 ..."` or `--inventory <ansible-inventory>` (parses
`ansible_host:` lines). Password from `--password PW` or `--generate` (strong 20-char alnum,
printed once).

### 2. Dry-run first
```bash
scripts/rotate-credentials.sh --generate --inventory ~/.config/agent-utilities/inventory.yaml --dry-run
```
Confirm the host list and intended action — nothing is changed.

### 3. Rotate
```bash
scripts/rotate-credentials.sh --generate \
    --inventory ~/.config/agent-utilities/inventory.yaml \
    --user genius [--idrac] [--out ~/Workspace/inventory/.env]
```
Each host: `chpasswd` the account → verify `passwd -S` shows `P` → (if `--idrac`) set BMC
user-2 + `ipmitool user test`. Capture the printed password. With `--out`, the credential
record is appended to a file — **that file must be gitignored** (plaintext secret).

### 4. Review the summary
`=== rotated N OK, M failed ===` plus per-host lines. Investigate any FAILED host (common
causes: sudo prompts, unreachable, or password tools crashing — see `references/usage.md`),
fix it, and re-run targeting just that host with the same `--password`.

## Safety notes
- SSH **key** auth is independent of the OS password, so a rotation never locks you out of
  SSH — only of console login. Recovery = re-run with a known `--password`.
- iDRAC IPMI user passwords cap at 16 bytes; use a 16-char password if `--idrac` and you
  need the full BMC password to match.
- Never commit the creds file. Add `.env`/secrets to `.gitignore`.

## See also — OIDC / service-account secret rotation
This skill rotates **host/OS (and iDRAC) passwords**. Rotating an **OIDC client secret**
(e.g. the `mcp-multiplexer` Keycloak client used for fleet service-account auth) is a
different runbook: the new secret — with the correct **`homelab`** realm in `OIDC_TOKEN_URL`,
not `master` — must fan to **every** consumer in one pass or you get a confusing partial
outage (a fleet-wide child 401 while the deployed mux looks fine): the swarm
`mcp-multiplexer` + `graph-os` (server+host) service envs, OpenBao `apps/mcp-multiplexer`,
and **every local `~/.claude.json`**. Full procedure + diagnosis: the agent-os-genesis
`references/homelab-ops-learnings.md` playbook ("Multiplexer → child service-account auth").
