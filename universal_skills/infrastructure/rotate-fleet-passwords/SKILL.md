---
name: rotate-fleet-passwords
domain: infrastructure
skill_type: skill
description: >-
  Set one unified OS-account password across many hosts over SSH (and optionally the
  in-band iDRAC/BMC user), verifying each and reporting a per-host summary. Use when the
  user wants to rotate/unify/change login passwords across a fleet, set a shared recovery
  credential, onboard hosts to a common password, or rotate BMC passwords. Triggers:
  "rotate passwords", "unified password across hosts", "change my password everywhere",
  "set a shared console password", "rotate the OpenBao agent-apps-rw token". Do NOT use for
  SSH key distribution (use ssh-bootstrap), arbitrary app/secret-store secrets (use
  secret-vault-manager), or single-host one-off passwd.
license: MIT
tags: [infra, security, credentials, password, ssh, ipmi, idrac, fleet, rotation, openbao, vault, token]
metadata:
  version: '1.3.1'
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

## OpenBao agent-apps-rw token rotation (6-month runbook)

A separate credential from the OS passwords above, but the **same rotation discipline**:
a single secret that, if it expires, takes the whole MCP fleet down. The homelab OpenBao
(`http://openbao.arpa`, KV v2) stores per-service secrets at `apps/<service>`; every
`*-mcp` service is injected with a shared **`agent-apps-rw`** token (policy `agent-apps-rw`:
`crud apps/data/*`, `list apps/metadata/*`) so connectors can read/write their secrets.
Rotate this token on a fixed 6-month cadence.

### Why it expired, and why a periodic token is the fix
The original token had a **finite TTL** (a fixed max lifetime). Service tokens default to
expiring; nothing renewed it, so when the TTL elapsed the token was revoked automatically.
Every `openbao-mcp` read and every connector write then failed (403/permission-denied),
which is the recent outage. A **periodic token** removes the absolute max-TTL: it can be
renewed indefinitely as long as it is renewed at least once within each `period` window
(`768h` ≈ 32 days here). So the fleet token never hits a hard expiry — it only needs a
heartbeat renewal inside the period (see cadence below), and you re-mint cleanly every
6 months for hygiene.

### Mint a fresh periodic token (break-glass)
Use the **root token** as break-glass only — `BAO_ROOT_TOKEN` lives in
`services/openbao/.env`. Mint a renewable periodic token scoped to the `agent-apps-rw`
policy:

```bash
# Break-glass: read the root token from the openbao service env (do NOT echo/commit it)
export BAO_ADDR=http://openbao.arpa
export BAO_ROOT_TOKEN="$(grep -E '^BAO_ROOT_TOKEN=' services/openbao/.env | cut -d= -f2-)"

# Mint a periodic, renewable token bound to the agent-apps-rw policy
NEW_TOKEN="$(curl -sf -X POST \
  -H "X-Vault-Token: ${BAO_ROOT_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"policies":["agent-apps-rw"],"period":"768h","renewable":true,"display_name":"agent-apps-rw","no_default_policy":true}' \
  "${BAO_ADDR}/v1/auth/token/create" | python3 -c 'import sys,json;print(json.load(sys.stdin)["auth"]["client_token"])')"
```

`period=768h` makes it periodic (no max-TTL); `renewable=true` lets the heartbeat extend it;
`no_default_policy=true` keeps it least-privilege (only `agent-apps-rw`).

### Stash + distribute the new token
Persist a copy of the new token in OpenBao itself so the next operator can find it
without break-glass, then push it to every consumer and redeploy:

```bash
# 1. Stash the new token at apps/_meta-agent-apps-rw on the `apps` KV v2 mount.
#    The policy grants `apps/data/*` and `apps/metadata/*` — the mount is `apps`,
#    NOT the default `secret`, so the API path is /v1/apps/data/<path>.
curl -sf -X POST -H "X-Vault-Token: ${BAO_ROOT_TOKEN}" \
  -d "{\"data\":{\"token\":\"${NEW_TOKEN}\",\"period\":\"768h\",\"minted\":\"$(date -u +%FT%TZ)\"}}" \
  "${BAO_ADDR}/v1/apps/data/_meta-agent-apps-rw"
```

- **Distribute to `apps/*`:** the token IS the read/write credential for the `apps/<service>`
  tree — nothing per-secret to rewrite; the new token simply replaces the old one wherever
  it is injected.
- **Distribute to each `*-mcp` service env:** update the injected token value (the
  `OPENBAO_TOKEN` / `BAO_TOKEN` / `VAULT_TOKEN` env var, whichever each compose file uses)
  for every `*-mcp` service so connectors and `openbao-mcp` pick up the new token.
- **Redeploy:** restart/redeploy the affected services so the new env takes effect
  (`docker compose up -d` / swarm `service update --force` on the manager node). Confirm
  `openbao-mcp` comes back healthy first, then the connectors.

### Renewal cadence (the heartbeat that prevents another expiry)
A periodic token must be renewed at least once per `period` (768h ≈ 32 days). Pick one:

```bash
# Self-renew using the token itself (run well inside the 768h window, e.g. weekly)
curl -sf -X POST -H "X-Vault-Token: ${NEW_TOKEN}" "${BAO_ADDR}/v1/auth/token/renew-self"
```

- **Heartbeat:** schedule `renew-self` weekly (cron / scheduled rotation job) so the token
  is always far from its period boundary — a single missed renewal then has weeks of slack.
- **Full re-mint:** re-run the *Mint* + *Distribute* steps every **6 months** for hygiene
  (fresh secret material), even though the periodic token would survive on heartbeats alone.
- Set a calendar reminder for both: weekly renew check, 6-month re-mint.

### Verify read/write on `apps/*`
Prove the new token actually has `agent-apps-rw` before declaring the rotation done:

```bash
# Token is valid + periodic (period shown, no hard expiry surprise)
curl -sf -H "X-Vault-Token: ${NEW_TOKEN}" "${BAO_ADDR}/v1/auth/token/lookup-self" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin)["data"];print("policies",d["policies"],"period",d.get("period"),"renewable",d["renewable"])'

# WRITE then READ a canary on the `apps` KV v2 mount (then delete it). Paths are
# apps/data/* (read/write) and apps/metadata/* (delete) — the mount granted by the
# `agent-apps-rw` policy, not the default `secret` mount.
curl -sf -X POST -H "X-Vault-Token: ${NEW_TOKEN}" \
  -d '{"data":{"canary":"ok"}}' "${BAO_ADDR}/v1/apps/data/_rotation-canary"
curl -sf -H "X-Vault-Token: ${NEW_TOKEN}" "${BAO_ADDR}/v1/apps/data/_rotation-canary" \
  | python3 -c 'import sys,json;print("read-back:",json.load(sys.stdin)["data"]["data"]["canary"])'
curl -sf -X DELETE -H "X-Vault-Token: ${NEW_TOKEN}" "${BAO_ADDR}/v1/apps/metadata/_rotation-canary"
```

Expect `policies ['agent-apps-rw']`, a non-empty `period`, `renewable True`, and
`read-back: ok`. Finally, hit one live `*-mcp` service (e.g. `openbao-mcp`) end-to-end to
confirm connectors read their real secrets. **Revoke the OLD token** once all services
are confirmed on the new one — revoke it **by its accessor** (you don't need the old
token's plaintext) via the root token:

```bash
# Revoke the OLD token by accessor. Find the accessor with `auth/token/lookup`
# (accessors are also listed under `auth/token/accessors`), then revoke it.
curl -sf -X POST -H "X-Vault-Token: ${BAO_ROOT_TOKEN}" \
  -d "{\"accessor\":\"${OLD_TOKEN_ACCESSOR}\"}" \
  "${BAO_ADDR}/v1/auth/token/revoke-accessor"
```

### Operator checklist
- [ ] Read `BAO_ROOT_TOKEN` from `services/openbao/.env` (break-glass; never echo/commit).
- [ ] Mint periodic token: `POST /v1/auth/token/create` `policies=[agent-apps-rw] period=768h renewable=true`.
- [ ] Stash new token at `apps/_meta-agent-apps-rw` (KV v2).
- [ ] Replace the injected token in **every `*-mcp` service env**.
- [ ] Redeploy affected services; confirm `openbao-mcp` healthy, then connectors.
- [ ] Schedule weekly `renew-self` heartbeat (within the 768h period).
- [ ] Verify: `lookup-self` shows `agent-apps-rw`/period/renewable, and the `apps/*` canary write+read+delete passes.
- [ ] Revoke the OLD token **by accessor** (`POST /v1/auth/token/revoke-accessor`).
- [ ] Set the 6-month re-mint calendar reminder.
