---
name: secret-vault-manager
description: >
  Secret Vault Manager atomic skill. Performs unsealing, initialization,
  secrets engine mounting, and KV secrets write/read operations on OpenBao (Vault) using openbao-mcp.
domain: infrastructure
tags:
  - vault
  - openbao
  - secrets
  - security
requires:
  - openbao-mcp
---

# Secret Vault Manager Skill

Stateless atomic operation to configure root credentials, manage initialization phases, and access path-level secrets in OpenBao/Vault engines.

## Prerequisites

- `openbao-mcp` — for executing OpenBao initialization, unsealing, sys engine, and KV logical operations.

## Steps

### Step 1: Health & Seal Check
Check seal status and initialization state on the vault server endpoints.

### Step 2: Initialize & Unseal Vault (Boot Phase)
If OpenBao/Vault is raw and uninitialized:
- Run initialization, capturing master shares and root token.
- Securely print master shares (or export securely) and store root token.
- Perform unseal steps by supplying necessary key shares.

### Step 3: Mount KV2 Secrets Engine
Configure dynamic secret engines:
- Enable the key-value version 2 (KV2) storage backend at target path (e.g. `/secret`).
- Setup custom path policies and access groups.

### Step 4: KV Secret Operations (CRUD)
Manage application credentials and settings:
- Write secrets containing dynamic database passwords, API tokens (e.g. GitLab PATs), or SSH parameters.
- Verify read permissions on registered paths.
