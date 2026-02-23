---
name: crypto-tools
description: A suite of cryptographic tools including bcrypt, hashing, HMAC, RSA generation, and string obfuscation.
tags: [crypto, security, hashing, tools]
---

# Crypto Tools

This skill provides a suite of tools for cryptographic operations, modeled after IT-Tools.

## Tools
*   `bcrypt`: Generate or verify bcrypt hashes.
*   `hash-text`: Hash text using standard algorithms (md5, sha1, sha256).
*   `hmac-generator`: Generate HMAC hashes.
*   `rsa-key-pair-generator`: Generate RSA public and private key pairs.
*   `string-obfuscator`: Obfuscate text.

## Usage
Run the script `scripts/main.py` with the desired command.

```bash
# Hash a password with bcrypt
python scripts/main.py bcrypt --password "my_secret_password"

# Hash a text with SHA256
python scripts/main.py hash-text --text "hello world" --algorithm "sha256"

# Generate RSA key pair
python scripts/main.py rsa-key-pair-generator --size 2048
```
