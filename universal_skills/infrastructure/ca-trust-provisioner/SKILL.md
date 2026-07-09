---
name: ca-trust-provisioner
skill_type: skill
description: >
  CA Trust Provisioner atomic skill. Bakes an enterprise / self-signed root-CA
  bundle into every touched system so deployments stop hitting self-signed-cert
  errors — installs the bundle into each host's trust store and emits the standard
  CA env contract (REQUESTS_CA_BUNDLE / SSL_CERT_FILE / NODE_EXTRA_CA_CERTS /
  GIT_SSL_CAINFO) for injection into every deployed service and the private
  registry. Triggers on "enterprise CA", "root CA bundle", "self-signed cert
  errors", "trust internal CA", "corporate proxy cert".
domain: infrastructure
tags:
  - tls
  - ca-bundle
  - enterprise
  - certificates
  - trust
requires:
  - tunnel-manager-mcp
metadata:
  version: '1.1.0'
---

# CA Trust Provisioner Skill

Stateless atomic operation that takes an enterprise / internal **root-CA bundle**
(PEM) and makes every system we touch trust it — so HTTPS calls to internal
endpoints (registry, GitLab, Vault, IdP, APIs behind a TLS-terminating proxy) do
**not** fail with self-signed / unknown-authority errors. This is the trust layer
the genesis flow runs when an operator supplies a corporate root CA; the standing
rule remains **never disable TLS verification** — install trust instead.

## Prerequisites

- `tunnel-manager-mcp` — run trust-store commands on each inventory host.
- A root-CA bundle (PEM). If none is supplied, auto-detect the system bundle
  (`/etc/ssl/certs/ca-certificates.crt` or `certifi`) and emit the env contract
  pointing at it (no host changes).

## Steps

### Step 1: Acquire & validate the bundle
Take the operator-provided PEM path/content (or auto-detect the system bundle).
Validate it parses as one or more X.509 certificates; record the SHA-256 fingerprint(s).

### Step 2: Install into each host trust store
For every host in the inventory, copy the bundle in and refresh the OS trust store —
Debian/Ubuntu: `/usr/local/share/ca-certificates/<name>.crt` + `update-ca-certificates`;
RHEL/Alma: `/etc/pki/ca-trust/source/anchors/` + `update-ca-trust extract`. Idempotent:
re-running with the same fingerprint is a no-op.

### Step 3: Emit the CA env contract (for every deployed service)
Produce the environment block that points language runtimes at the bundle, to be
injected into every deployed stack/container env (and the local toolchain):

```
REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # Python requests/urllib3
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt        # OpenSSL / many libs
NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt   # Node.js
GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt        # git over HTTPS
```

(After Step 2 the enterprise root is folded into the OS bundle, so a single path
covers all runtimes.) For container images that don't ship the host bundle, also
mount it read-only into the container at the same path.

### Step 4: Trust the private registry on the orchestrator
Ensure the container runtime trusts the registry's TLS:
- Docker/Swarm: place the CA at `/etc/docker/certs.d/<registry>/ca.crt` per node.
- Podman: `/etc/containers/certs.d/<registry>/ca.crt`.
- Kubernetes/RKE2: add the CA to the node trust store (Step 2) + the registry config.

### Step 5: Verify
From a host, confirm an HTTPS call to an internal endpoint succeeds **with**
verification on (e.g. `curl https://<internal-endpoint>` returns without a cert
error, `python -c "import requests; requests.get('https://…')"` succeeds), and that
the runtime can pull from the private registry.

## Execution

Atomic skill — run the steps in order via `tunnel-manager-mcp` (per-host file copy +
`update-ca-certificates`/`update-ca-trust` + registry cert placement). The emitted
env contract (Step 3) is handed back to the deploy step so each service stack injects
it (sourced alongside the service's other env from OpenBao/.env). Re-runnable.

> **Execution:** If graph-os is reachable, offload the per-host fan-out via
> `graph_orchestrate action=execute_agent` (or `kg-delegate`); otherwise run
> the steps natively across the inventory hosts.
