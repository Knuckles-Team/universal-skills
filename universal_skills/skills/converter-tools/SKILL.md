---
name: converter-tools
description: A suite of data and format conversion tools including Base64, JSON, YAML, TOML, and more.
tags: [converter, format, dev, tools]
---

# Converter Tools

This skill provides a suite of tools for data and format conversion, modeled after IT-Tools.

## Tools
*   `yaml-to-json`: Convert YAML formatted strings to JSON.
*   `json-to-toml`: Convert JSON formatted strings to TOML.
*   `base64`: Encode or decode text to/from Base64.
*   `binary`: Encode or decode text to/from Binary.
*   `url`: URL encode or decode a string.

## Usage
Run the script `scripts/main.py` with the desired command.

```bash
# Convert YAML to JSON
python scripts/main.py yaml-to-json --yaml "key: value"

# Base64 encode a string
python scripts/main.py base64 --text "hello world"
```
