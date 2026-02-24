---
name: developer-utilities
description: "A consolidated suite of developer utilities including formatting, conversion, generation, cryptographic, and networking tools."
categories: [Development, Productivity, System & Infrastructure, Data & Documents]
tags: [development, utilities, parsing, tools, converter, generator, crypto, network]
---

# Developer Utilities

## Overview

This skill provides a consolidated suite of tools modeled after IT-Tools, combining development, conversion, generation, cryptography, and network capabilities into a single interface.

## Capabilities / Tools

### Development & Parsing (`scripts/dev_tools.py`)
*   `jwt`: Parse and decode JWT tokens.
*   `sql-format`: Format/Prettify SQL queries.
*   `regex`: Test regular expressions against text.
*   `user-agent`: Parse User-Agent strings.
*   `json-minify`: Compress JSON.
*   `json-diff`: Unified diff of two JSON strings.

### Conversion (`scripts/converter_tools.py`)
*   `yaml-to-json`: Convert YAML formatted strings to JSON.
*   `json-to-toml`: Convert JSON formatted strings to TOML.
*   `base64`: Encode or decode text to/from Base64.
*   `binary`: Encode or decode text to/from Binary.
*   `url`: URL encode or decode a string.

### Generators (`scripts/generator_tools.py`)
*   `uuid`: Generate UUIDs (v1 or v4).
*   `ulid`: Generate ULIDs.
*   `token`: Generate secure random tokens.
*   `otp`: Generate 6-digit one-time passwords.
*   `password`: Generate secure passwords with custom character sets.
*   `lorem`: Generate Lorem Ipsum text.

### Cryptography (`scripts/crypto_tools.py`)
*   `bcrypt`: Generate or verify bcrypt hashes.
*   `hash-text`: Hash text using standard algorithms (md5, sha1, sha256).
*   `hmac-generator`: Generate HMAC hashes.
*   `rsa-key-pair-generator`: Generate RSA public and private key pairs.
*   `string-obfuscator`: Obfuscate text.

### Network (`scripts/network_tools.py`)
*   `subnet`: IPv4 Subnet Calculator.
*   `mac`: Generate a random MAC address.
*   `http-status`: Get information about an HTTP Status Code.

## Usage

Run the scripts in the `scripts/` directory with the desired command.

```bash
# Example executions
python scripts/dev_tools.py jwt --token "eyJhb..."
python scripts/converter_tools.py yaml-to-json --yaml "key: value"
python scripts/generator_tools.py uuid
python scripts/crypto_tools.py hash-text --text "hello world" --algorithm "sha256"
python scripts/network_tools.py subnet --cidr "192.168.1.0/24"
```
