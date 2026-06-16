---
name: dns-migration-utility
description: >
  DNS Migration Utility atomic skill. Extracts DNS rewrites, hosts lists, and zone files
  from legacy resolvers (AdGuard Home, Pi-hole, bind9) and prepares them for authoritative Technitium DNS integration.
domain: infrastructure
tags:
  - dns
  - migration
  - network
requires:
  - systems-manager-mcp
---

# DNS Migration Utility Skill

Stateless atomic operation to ingest legacy DNS configuration formats and convert them into unified, brand-agnostic record payloads.

## Prerequisites

- `systems-manager-mcp` — for reading local configuration backups, host lists, or zone files.

## Steps

### Step 1: Ingest Legacy Configuration Sources
Load DNS zone or rewrite backups based on target source-format:
- **AdGuard Home**: Query active rewrites via API or load `AdGuardHome.yaml` configuration.
- **Pi-hole**: Parse `custom.list` or blocklist configs.
- **bind9 / dnsmasq**: Ingest RFC-compliant zone files or custom conf files.

### Step 2: Clean and Normalize Records
Parse host names, domains, record types (A, AAAA, CNAME, TXT), and target IP addresses:
- Deduplicate conflicting domain-to-IP definitions.
- Validate domain names against RFC rules.
- Filter out local loopback or private ranges that should not be mapped.

### Step 3: Format Normalized Export Payload
Convert the parsed DNS records into a unified, brand-agnostic format for authoritative Technitium zone import:
- Output lists of type: `{"domain": "service.arpa", "type": "A", "value": "10.0.0.10", "ttl": 3600}`

## Resources

- `scripts/migrate_dns.py` — extracts and normalizes records from legacy resolver configs (AdGuard Home, Pi-hole, bind9, dnsmasq) into the unified A/CNAME export payload for authoritative Technitium import.
