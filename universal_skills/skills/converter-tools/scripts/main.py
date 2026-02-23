#!/usr/bin/env python3
import argparse
import json
import base64
import urllib.parse

try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None


def yaml_to_json(yaml_str):
    if yaml is None:
        return {"error": "PyYAML is not installed."}
    try:
        data = yaml.safe_load(yaml_str)
        return {"json": json.dumps(data, indent=2)}
    except Exception as e:
        return {"error": str(e)}


def json_to_toml(json_str):
    if toml is None:
        return {"error": "toml library is not installed."}
    try:
        data = json.loads(json_str)
        return {"toml": toml.dumps(data)}
    except Exception as e:
        return {"error": str(e)}


def base64_encode(text):
    return {"encoded": base64.b64encode(text.encode("utf-8")).decode("utf-8")}


def base64_decode(text):
    try:
        return {"decoded": base64.b64decode(text.encode("utf-8")).decode("utf-8")}
    except Exception as e:
        return {"error": str(e)}


def text_to_binary(text):
    return {"binary": " ".join(format(ord(c), "08b") for c in text)}


def binary_to_text(binary_str):
    try:
        return {"text": "".join(chr(int(b, 2)) for b in binary_str.split(" "))}
    except Exception as e:
        return {"error": str(e)}


def url_encode(text):
    return {"encoded": urllib.parse.quote(text)}


def url_decode(text):
    return {"decoded": urllib.parse.unquote(text)}


def main():
    parser = argparse.ArgumentParser(description="Converter Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    y2j = subparsers.add_parser("yaml-to-json")
    y2j.add_argument("--yaml", required=True)

    j2t = subparsers.add_parser("json-to-toml")
    j2t.add_argument("--json", required=True)

    b64 = subparsers.add_parser("base64")
    b64.add_argument("--text", required=True)
    b64.add_argument("--decode", action="store_true")

    bin_parser = subparsers.add_parser("binary")
    bin_parser.add_argument("--text", required=True)
    bin_parser.add_argument("--decode", action="store_true")

    url_parser = subparsers.add_parser("url")
    url_parser.add_argument("--text", required=True)
    url_parser.add_argument("--decode", action="store_true")

    args = parser.parse_args()
    result = {}

    if args.command == "yaml-to-json":
        result = yaml_to_json(args.yaml)
    elif args.command == "json-to-toml":
        result = json_to_toml(args.json)
    elif args.command == "base64":
        if args.decode:
            result = base64_decode(args.text)
        else:
            result = base64_encode(args.text)
    elif args.command == "binary":
        if args.decode:
            result = binary_to_text(args.text)
        else:
            result = text_to_binary(args.text)
    elif args.command == "url":
        if args.decode:
            result = url_decode(args.text)
        else:
            result = url_encode(args.text)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
