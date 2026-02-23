---
name: network-tools
description: A suite of networking tools including Subnet calculator, MAC address generator, and HTTP Status Codes.
tags: [network, system, admin, tools]
---

# Network Tools

This skill provides a suite of networking tools, modeled after IT-Tools.

## Tools
*   `subnet`: IPv4 Subnet Calculator. Given a CIDR, it calculates network details.
*   `mac`: Generate a random MAC address, optionally with a specified prefix.
*   `http-status`: Get information about an HTTP Status Code.

## Usage
Run the script `scripts/main.py` with the desired command.

```bash
# Calculate Subnet
python scripts/main.py subnet --cidr "192.168.1.0/24"

# Generate MAC address
python scripts/main.py mac --prefix "00:1A:2B"

# HTTP Status Info
python scripts/main.py http-status --code 404
```
