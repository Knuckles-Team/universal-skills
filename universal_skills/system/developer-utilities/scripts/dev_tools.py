#!/usr/bin/env python3
import argparse
import json
import re
import base64
from difflib import unified_diff

try:
    import sqlparse
except ImportError:
    sqlparse = None

try:
    from user_agents import parse as parse_user_agent
except ImportError:
    parse_user_agent = None


def parse_jwt(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {"error": "Invalid JWT token format"}

        def decode_part(part):
            part += "=" * (-len(part) % 4)
            return json.loads(base64.urlsafe_b64decode(part).decode("utf-8"))

        return {
            "header": decode_part(parts[0]),
            "payload": decode_part(parts[1]),
            "signature": parts[2],
        }
    except Exception as e:
        return {"error": str(e)}


def prettify_sql(sql_query):
    if sqlparse is None:
        return {"error": "sqlparse library is not installed."}
    try:
        formatted = sqlparse.format(sql_query, reindent=True, keyword_case="upper")
        return {"formatted_sql": formatted}
    except Exception as e:
        return {"error": str(e)}


def test_regex(pattern, text, flags=0):
    try:
        matches = list(re.finditer(pattern, text, flags))
        return {
            "matches": [
                {
                    "match": m.group(0),
                    "start": m.start(),
                    "end": m.end(),
                    "groups": m.groups(),
                }
                for m in matches
            ],
            "count": len(matches),
        }
    except Exception as e:
        return {"error": str(e)}


def parse_ua(user_agent_string):
    if parse_user_agent is None:
        return {"error": "user_agents library is not installed."}
    try:
        ua = parse_user_agent(user_agent_string)
        return {
            "browser": {
                "family": ua.browser.family,
                "version": ua.browser.version_string,
            },
            "os": {"family": ua.os.family, "version": ua.os.version_string},
            "device": {
                "family": ua.device.family,
                "brand": ua.device.brand,
                "model": ua.device.model,
                "is_mobile": ua.is_mobile,
                "is_tablet": ua.is_tablet,
                "is_pc": ua.is_pc,
                "is_bot": ua.is_bot,
            },
        }
    except Exception as e:
        return {"error": str(e)}


def minify_json(json_str):
    try:
        parsed = json.loads(json_str)
        return {"minified": json.dumps(parsed, separators=(",", ":"))}
    except Exception as e:
        return {"error": str(e)}


def diff_json(json1, json2):
    try:
        obj1 = json.loads(json1)
        obj2 = json.loads(json2)

        # Format neatly to diff line by line
        str1 = json.dumps(obj1, indent=2).splitlines(keepends=True)
        str2 = json.dumps(obj2, indent=2).splitlines(keepends=True)

        diff = list(unified_diff(str1, str2, fromfile="json1", tofile="json2"))
        return {"diff": "".join(diff)}
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Dev Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    jwt = subparsers.add_parser("jwt")
    jwt.add_argument("--token", required=True)

    sql = subparsers.add_parser("sql-format", aliases=["sql_format"])
    sql.add_argument("--query", required=True)

    regex = subparsers.add_parser("regex")
    regex.add_argument("--pattern", required=True)
    regex.add_argument("--text", required=True)
    regex.add_argument("--ignore-case", "--ignore_case", action="store_true")

    # Assuming 'pass' is a new command for password generation or similar,
    # based on the new arguments provided in the instruction.
    # If these arguments belong to an existing command, please clarify.
    pass_parser = subparsers.add_parser("pass")
    pass_parser.add_argument("--no-upper", "--no_upper", action="store_true")
    pass_parser.add_argument("--no-lower", "--no_lower", action="store_true")
    pass_parser.add_argument("--no-numbers", "--no_numbers", action="store_true")
    pass_parser.add_argument("--no-symbols", "--no_symbols", action="store_true")

    ua = subparsers.add_parser("user-agent", aliases=["user_agent"])
    ua.add_argument("--ua", required=True)

    jmin = subparsers.add_parser("json-minify", aliases=["json_minify"])
    jmin.add_argument("--json", required=True)

    jdiff = subparsers.add_parser("json-diff")
    jdiff.add_argument("--json1", required=True)
    jdiff.add_argument("--json2", required=True)

    args = parser.parse_args()
    result = {}

    if args.command == "jwt":
        result = parse_jwt(args.token)
    elif args.command == "sql-format":
        result = prettify_sql(args.query)
    elif args.command == "regex":
        flags = re.IGNORECASE if args.ignore_case else 0
        result = test_regex(args.pattern, args.text, flags)
    elif args.command == "user-agent":
        result = parse_ua(args.ua)
    elif args.command == "json-minify":
        result = minify_json(args.json)
    elif args.command == "json-diff":
        result = diff_json(args.json1, args.json2)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
