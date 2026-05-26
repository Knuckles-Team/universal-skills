---
name: dns-record-manager
description: >
  DNS Record Manager atomic skill. Manages authoritative zones and records (A, CNAME, TXT)
  on Technitium DNS primary server using technitium-dns-mcp.
domain: infrastructure
tags:
  - dns
  - technitium
  - networking
  - records
requires:
  - technitium-dns-mcp
---

# DNS Record Manager Skill

Stateless atomic operation to perform CRUD actions on authoritative DNS records and zones.

## Prerequisites

- `technitium-dns-mcp` — for direct interaction with the primary authoritative DNS service API.

## Steps

### Step 1: Initialize / Validate Zone
Ensure target zone (e.g. `arpa` or `home.arpa`) exists on the authoritative server. If missing:
- Create the primary authoritative zone.
- Configure zone options (SOA, TTL, dynamic updates).

### Step 2: Manage Record Entries
Coordinate record-level changes based on input parameters (action: add, update, delete):
- **A Records**: Map service subdomain (e.g. `gitlab.arpa`) to target host node IP (e.g. `10.0.0.12`).
- **CNAME Records**: Map subdomains to canonical host names.
- **TXT Records**: Map authentication, verification, or service token mappings.
- **PTR / DNSSEC**: Set up reverse mapping or sign zones as needed.

### Step 3: Validate Records Resolution
Verify that record changes are active on the primary resolver immediately:
- Query zone records to check successful insertion/removal.
