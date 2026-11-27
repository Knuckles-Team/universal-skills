---
name: ca-trust-provisioner
skill_type: skill
description: >-
  Bake an enterprise or self-signed root-CA bundle into every touched host trust store and emit the CA env contract (REQUESTS_CA_BUNDLE, SSL_CERT_FILE, NODE_EXTRA_CA_CERTS, GIT_SSL_CAINFO) for deployed services. Use when you see self-signed cert errors, need to trust an internal CA, or a corporate proxy cert breaks TLS. Do NOT use to issue certificates.
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
  version: '1.7.0'
---

# CA Trust Provisioner Skill

Scope: CA Trust Provisioner atomic skill. Bakes an enterprise / self-signed root-CA bundle into every touched system so deployments stop hitting self-signed-cert errors — installs the bundle into each host's trust store and emits the standard CA env contract (REQUESTS_CA_BUNDLE / SSL_CERT_FILE / NODE_EXTRA_CA_CERTS / GIT_SSL_CAINFO) for injection into every deployed service and the private registry. Triggers on "enterprise CA", "root CA bundle", "self-signed cert errors", "trust internal CA", "corporate proxy cert".

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

1. Acquire the root-CA bundle PEM and validate it parses as X.509 (Step 1). Verify that `openssl x509 -in <bundle.pem> -noout -fingerprint -sha256` prints a SHA-256 fingerprint for the certificate.
2. Install the bundle into each inventory host's trust store through `tunnel-manager-mcp` with `update-ca-certificates` or `update-ca-trust extract` (Step 2). Verify that `openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt <bundle.pem>` succeeds on every host.
3. Emit the CA env contract `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS` and `GIT_SSL_CAINFO` for every deployed service (Step 3). Verify that all four variables point at an existing bundle path with `ls -l`.
4. Place the CA at `/etc/docker/certs.d/<registry>/ca.crt` (or the Podman equivalent) on each node (Step 4). Verify that the file exists on each node with `ls`.
5. Test an HTTPS call to an internal endpoint with verification on, using `curl https://<internal-endpoint>` (Step 5). Verify that the call returns without a certificate error and that the runtime can pull from the private registry.

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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `openssl x509` reports "unable to load certificate" | The file is not PEM or holds a chain with extra text | Convert the file with `openssl x509 -inform DER -in <file> -out bundle.pem` or strip non-certificate text, then validate again |
| `curl` still reports an unknown authority | The trust store was not refreshed or the tool uses its own bundle | Rerun `update-ca-certificates` (or `update-ca-trust extract`) on the host and set `SSL_CERT_FILE` to the system bundle path |
| Registry pull fails with x509 error | The CA is not in `certs.d/<registry>/` for the runtime | Copy the CA to `/etc/docker/certs.d/<registry>/ca.crt` on that node and restart the container runtime |
| A containerized service still fails TLS | The image lacks the host bundle | Mount the bundle read-only at the same path in the container and set the env contract in the stack |


## Execution

Atomic skill — run the steps in order via `tunnel-manager-mcp` (per-host file copy +
`update-ca-certificates`/`update-ca-trust` + registry cert placement). The emitted
env contract (Step 3) is handed back to the deploy step so each service stack injects
it (sourced alongside the service's other env from OpenBao/.env). Re-runnable.

> **Execution:** If arbora is reachable, offload the per-host fan-out via
> `graph_orchestrate action=execute_agent` (or `kg-delegate`); otherwise run
> the steps natively across the inventory hosts.
