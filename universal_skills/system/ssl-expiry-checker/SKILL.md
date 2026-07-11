---
name: ssl-expiry-checker
skill_type: skill
description: >
  Network SSL/TLS expiry checker atomic skill. Connects to targets, parses TLS certs,
  and returns expiration days and security grades.
domain: system
license: MIT
tags: [security, network, ssl, monitoring, tls]
metadata:
  version: '1.2.0'
  author: Genius
requires:
  - systems-manager-mcp
---

# SSL Expiry Checker Skill

Stateless atomic operation to query target domain endpoints, establish TLS handshakes, extract active SSL/TLS peer certificate parameters, and evaluate expiration dates and security compliance grades.

## Prerequisites

- `systems-manager-mcp` — or system tools with socket network egress capability to perform TCP dial and TLS certificate inspection.

## Steps

### Step 1: resolve_target_endpoints
Parse and prepare the target network addresses for connection:
- Parse the input parameters which must contain:
  - `domains`: List of domain names or hostnames to check (e.g. `gitlab.arpa`, `google.com`)
  - `port`: Optional integer target port (default: 443)
  - `timeout_seconds`: Optional integer connection timeout (default: 5)
- Perform DNS lookup / resolution check for each target domain to verify it is reachable and active.
- Skip hostnames that do not resolve, recording DNS errors in the diagnostics.

### Step 2: fetch_tls_handshake [depends_on: resolve_target_endpoints]
Establish socket connections and extract active TLS certificates from the targets:
- For each resolved domain, execute a secure TCP connection to the specified port.
- Initiate a standard TLS client handshake, capturing the peer SSL certificate chain.
- Read and decode the certificate structure to extract core attributes:
  - Subject Common Name (CN) and Subject Alternative Names (SANs)
  - Issuer Name (e.g. Let's Encrypt, custom CA)
  - Serial Number and Signature Algorithm (e.g. SHA256-RSA)
  - `notBefore` (Valid From) date and `notAfter` (Valid To) date.
- Gracefully handle connection timeouts, refused connections, or SSL handshake failures (e.g. untrusted CA warnings or self-signed cert blocks).

### Step 3: evaluate_ssl_status [depends_on: fetch_tls_handshake]
Analyze certificate validity windows and assess alert levels based on remaining lifetimes:
- Calculate the precise number of days remaining until the certificate expires (`notAfter` timestamp minus current UTC time).
- Assign an operational security grade based on the expiration timeline:
  - **EXPIRED**: Expiration date has already passed. Action required immediately.
  - **CRITICAL**: Expiration is within 7 days. Critical renew warning.
  - **WARNING**: Expiration is within 14 days. Routine renew warning.
  - **OK**: Certificate is valid for 15+ days.
- Compile and return a structured JSON evaluation report:
  - `domain`: String (target name)
  - `status`: String ("OK", "WARNING", "CRITICAL", "EXPIRED", "ERROR")
  - `days_remaining`: Int (days until expiration)
  - `issuer`: String (CA issuer details)
  - `valid_to`: String (ISO-8601 validity end date)
  - `signature_algorithm`: String (e.g. sha256WithRSAEncryption)
  - `error_message`: String (null or connection/TLS handshake failure details)
- Print an actionable warning if any domain falls under WARNING, CRITICAL, or EXPIRED.
