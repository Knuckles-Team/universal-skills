---
name: mcp-endpoint-oidc-tls-hardening
skill_type: workflow
description: >-
  Enforce OIDC bearer validation and verified TLS on a Kubernetes-hosted MCP
  endpoint using AgentConfig identity, deployment, certificate, trust, and
  verifier profile references. Use when an MCP listener must reject anonymous or
  wrong-audience calls and serve through a trusted HTTPS endpoint. Do not use to
  create or rotate an OIDC client, store raw credentials, or bypass certificate
  verification.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: apply profile-driven OIDC resource-server and TLS enforcement to an MCP endpoint
  execution_mode: sequential
  specialist_ids:
    - config-agent
    - identity-agent
    - deployer-agent
    - tls-agent
    - verify-agent
    - evidence-agent
  tool_assignments:
    config-agent: [graph_configure]
    identity-agent: [tun_tm_remote]
    deployer-agent: [cnt_cm_k8s_config]
    tls-agent: [cnt_cm_k8s_config]
    verify-agent: [tun_tm_remote]
    evidence-agent: [graph_write]
tags: [oidc, jwt, tls, mcp, hardening, bearer-auth, kubernetes]
concept: CONCEPT:INFRA-001
requires:
  - graph-os
  - tunnel-manager-mcp
  - container-manager-mcp
metadata:
  version: '1.2.1'
---

# MCP endpoint OIDC and TLS hardening

**CONCEPT:INFRA-001**

Compose six exact MCP operations. All environment values remain in AgentConfig or
the referenced providers. Workflow inputs and retained evidence contain opaque
reference names and digests only.

## Runtime inputs

Require these named references:

- `oidc_resource_server_profile_ref`: issuer, discovery/JWKS source, accepted
  audience, algorithms, clock-skew policy, and claim requirements;
- `endpoint_deployment_ref`: namespace, workload, service, and ingress identity;
- `certificate_profile_ref`: issuer, DNS names, renewal policy, and secret sink;
- `client_trust_profile_ref`: complete CA bundle and runtime trust variables;
- `verification_profile_ref`: bounded issuer, audience, anonymous-call, and TLS
  chain checks;
- `transport_policy_ref`: HTTPS-only cutover or an explicitly bounded migration
  window.

Reject a raw endpoint, realm, audience, hostname, namespace, credential, CA path,
local path, or manifest in the workflow payload. Reject unresolved references and
profiles that disable TLS verification. OIDC client provisioning and secret
rotation are separate governed capabilities and must be complete before this
workflow starts.

## Steps

### Step 0: validate_profiles [mcp_tool: graph_configure]

Run `action=config_doctor` and require affirmative status for every referenced
identity, deployment, certificate, trust, and verification profile. Record only
profile digests and capability status.

Expected: `validated_profile_digests`

### Step 1: verify_identity_provider [depends_on: validate_profiles] [mcp_tool: tun_tm_remote]

Run the approved identity-provider check from `verification_profile_ref`. Require
verified discovery metadata or JWKS retrieval, exact issuer matching, an allowed
algorithm set, and a token whose audience satisfies the resource-server policy.
The provider must redact tokens, URLs, claims that identify a principal, and raw
responses.

Expected: `identity_provider_verified`

### Step 2: configure_bearer_validation [depends_on: verify_identity_provider] [mcp_tool: cnt_cm_k8s_config]

Apply the resource-server settings from `oidc_resource_server_profile_ref` to the
workload selected by `endpoint_deployment_ref`. The deployment adapter resolves
all concrete values internally. Roll the workload and require healthy convergence.

Expected: `bearer_validation_applied`

### Step 3: configure_tls [depends_on: configure_bearer_validation] [mcp_tool: cnt_cm_k8s_config]

Materialize the certificate and ingress/service changes named by
`certificate_profile_ref`, and bind client trust through
`client_trust_profile_ref`. Follow `transport_policy_ref`; do not keep plaintext
serving enabled unless that policy authorizes a bounded migration window.

Expected: `certificate_ready, tls_route_ready, trust_profile_digest`

### Step 4: verify_enforcement [depends_on: configure_tls] [mcp_tool: tun_tm_remote]

Run the approved end-to-end verifier. Require all of the following:

- a valid token with the configured audience succeeds;
- no token is rejected;
- a wrong-audience token is rejected;
- the full TLS chain validates against the configured trust profile;
- expiry, hostname, and redirect policy match the referenced contracts.

Fail closed on an ambiguous result. Do not use insecure client flags or retain
tokens, endpoints, certificate subjects, local trust paths, or response bodies.

Expected: `enforcement_verified`

### Step 5: persist_outcome [depends_on: verify_enforcement] [mcp_tool: graph_write]

Persist the workflow status, profile digests, policy decisions, bounded aggregate
checks, and timestamps. Never persist environment values, identities, credentials,
hostnames, addresses, namespaces, local paths, or certificate material.

Expected: `hardening_evidence_ref`

## Safety invariants

- Never create, rotate, display, or persist a client secret in this workflow.
- Never disable TLS verification or weaken hostname validation.
- Do not report completion until positive and negative authorization checks pass.
- Roll back the profile-owned deployment change when convergence or verification
  fails; retain only rollback status and profile digests.
- Treat every environment-specific value as provider-owned runtime data.

## Execution

Run the steps strictly in dependency order. No step is parallel because each
validates state required by the next.

**Execution:** If graph-os is reachable, offload the whole DAG via
`graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true
parallel/swarm execution. Otherwise execute the steps natively in dependency
order: run steps with no unmet `depends_on` in parallel, then their dependents.
