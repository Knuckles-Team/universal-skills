---
name: generator-tools
description: A suite of generation tools including UUID, ULID, Tokens, OTP, Passwords, and Lorem Ipsum.
categories: [Productivity]
tags: [generator, random, dev, tools]
---

# Generator Tools

## Overview

This skill provides a suite of tools for generating various strings and identifiers, modeled after IT-Tools.

## Capabilities/Tools
*   `uuid`: Generate UUIDs (v1 or v4).
*   `ulid`: Generate ULIDs.
*   `token`: Generate secure random tokens.
*   `otp`: Generate 6-digit one-time passwords.
*   `password`: Generate secure passwords with custom character sets.
*   `lorem`: Generate Lorem Ipsum text.

## Usage
Run the script `scripts/main.py` with the desired command.

```bash
# Generate a UUIDv4
python scripts/main.py uuid

# Generate a 32-character secure token
python scripts/main.py token --length 32 --chars hex

# Generate a password without symbols
python scripts/main.py password --length 20 --no-symbols
```
