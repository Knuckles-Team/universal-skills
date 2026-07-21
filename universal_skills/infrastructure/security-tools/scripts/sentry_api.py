#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request

from universal_skills._security.http import (
    SafeHttpError,
    SafeHttpStatus,
    UrlPolicy,
    open_json,
)

DEFAULT_BASE_URL = "https://sentry.io"
DEFAULT_ORG = "your-org"
DEFAULT_PROJECT = "your-project"
MAX_LIMIT = 50
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
OBJECT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
LOCAL_PATH_RE = re.compile(
    r"(?i)(?:[a-z]:[\\/](?:users|workspace)[\\/][^\s:'\"]+|"
    r"/(?:home|users|mnt)/[^\s:'\"]+)"
)


def redact_string(value):
    value = EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    value = IP_RE.sub("[REDACTED_IP]", value)
    value = LOCAL_PATH_RE.sub("[REDACTED_PATH]", value)
    return value


def redact_data(value):
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            normalized = key.lower()
            if normalized in {"email", "ip", "ip_address"} or any(
                marker in normalized
                for marker in ("authorization", "cookie", "password", "secret", "token")
            ):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_data(item)
        return redacted
    return value


def next_cursor(link_header):
    if not link_header or len(link_header) > 8_192:
        return None
    for part in link_header.split(","):
        if 'rel="next"' in part and 'results="true"' in part:
            match = re.search(r'cursor="([^"]+)"', part)
            if match:
                return match.group(1)
    return None


def request_json(url, token, retries=1):
    if (
        not isinstance(token, str)
        or not token
        or len(token) > 65_536
        or any(character in token for character in "\x00\r\n")
    ):
        raise RuntimeError("Sentry credential is invalid")
    if not isinstance(retries, int) or not 0 <= retries <= 3:
        raise RuntimeError("Sentry retry boundary is invalid")
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    attempt = 0
    while True:
        try:
            host = (urlsplit(url).hostname or "").lower().rstrip(".")
            data, response = open_json(
                req,
                policy=UrlPolicy(
                    frozenset({host}),
                    allow_private_hosts=frozenset({host}),
                    allow_http_loopback=True,
                ),
                timeout=30,
                max_bytes=8 * 1024 * 1024,
            )
            return data, response.headers
        except SafeHttpStatus as err:
            if attempt < retries and (err.status >= 500 or err.status == 429):
                attempt += 1
                time.sleep(1)
                continue
            raise RuntimeError(f"Remote service returned HTTP {err.status}") from err
        except (SafeHttpError, ValueError) as err:
            if attempt < retries:
                attempt += 1
                time.sleep(1)
                continue
            raise RuntimeError("Remote service request failed") from err


def build_url(base_url, path, params=None):
    if (
        not isinstance(path, str)
        or not path.startswith("/api/0/")
        or ".." in path
        or any(character in path for character in "\\\r\n#")
        or len(path) > 4_096
    ):
        raise RuntimeError("Sentry API path is invalid")
    base = base_url.rstrip("/")
    url = f"{base}{path}"
    if params:
        url = f"{url}?{urlencode(params, doseq=True)}"
    return url


def paged_get(base_url, path, params, token, limit):
    results = []
    cursor = None
    while len(results) < limit:
        page_params = dict(params)
        page_params["per_page"] = min(MAX_LIMIT, limit - len(results))
        if cursor:
            page_params["cursor"] = cursor
        url = build_url(base_url, path, page_params)
        data, headers = request_json(url, token)
        if not data:
            break
        if not isinstance(data, list):
            raise RuntimeError("Sentry response shape is invalid")
        results.extend(data)
        cursor = next_cursor(headers.get("Link"))
        if not cursor:
            break
    return results[:limit]


def require_org_project(org, project):
    if (
        org == DEFAULT_ORG
        or project == DEFAULT_PROJECT
        or SLUG_RE.fullmatch(str(org)) is None
        or SLUG_RE.fullmatch(str(project)) is None
    ):
        raise RuntimeError(
            "Missing org/project. Set SENTRY_ORG and SENTRY_PROJECT or pass --org/--project."
        )


def handle_list_issues(args, token, base_url):
    require_org_project(args.org, args.project)
    limit = max(1, min(args.limit, MAX_LIMIT))
    params = {
        "statsPeriod": args.time_range,
        "environment": args.environment,
    }
    if args.query:
        params["query"] = args.query

    path = f"/api/0/projects/{args.org}/{args.project}/issues/"
    issues = paged_get(base_url, path, params, token, limit)
    return issues


def handle_issue_detail(args, token, base_url):
    if OBJECT_ID_RE.fullmatch(str(args.issue_id)) is None:
        raise RuntimeError("Issue identifier is invalid")
    path = f"/api/0/issues/{args.issue_id}/"
    url = build_url(base_url, path)
    data, _ = request_json(url, token)
    return data


def handle_issue_events(args, token, base_url):
    if OBJECT_ID_RE.fullmatch(str(args.issue_id)) is None:
        raise RuntimeError("Issue identifier is invalid")
    limit = max(1, min(args.limit, MAX_LIMIT))
    path = f"/api/0/issues/{args.issue_id}/events/"
    events = paged_get(base_url, path, {}, token, limit)
    return events


def handle_event_detail(args, token, base_url):
    require_org_project(args.org, args.project)
    if OBJECT_ID_RE.fullmatch(str(args.event_id)) is None:
        raise RuntimeError("Event identifier is invalid")
    path = f"/api/0/projects/{args.org}/{args.project}/events/{args.event_id}/"
    url = build_url(base_url, path)
    data, _ = request_json(url, token)
    if data:
        data = dict(data)
        data.pop("entries", None)
    return data


def build_parser():
    parser = argparse.ArgumentParser(
        description="Read-only Sentry API helper for issues and events"
    )
    parser.add_argument(
        "--base-url",
        "--base_url",
        default=os.environ.get("SENTRY_BASE_URL", DEFAULT_BASE_URL),
        help="Sentry base URL (default: https://sentry.io)",
    )
    parser.add_argument(
        "--org",
        default=os.environ.get("SENTRY_ORG", DEFAULT_ORG),
        help="Sentry org slug",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("SENTRY_PROJECT", DEFAULT_PROJECT),
        help="Sentry project slug",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_issues = subparsers.add_parser("list-issues", help="List issues")
    list_issues.add_argument("--time-range", "--time_range", default="24h")
    list_issues.add_argument("--environment", default="prod")
    list_issues.add_argument("--query", default="")
    list_issues.add_argument("--limit", type=int, default=20)

    issue_detail = subparsers.add_parser("issue-detail", help="Issue detail")
    issue_detail.add_argument("issue_id")

    issue_events = subparsers.add_parser("issue-events", help="Issue events")
    issue_events.add_argument("issue_id")
    issue_events.add_argument("--limit", type=int, default=20)

    event_detail = subparsers.add_parser("event-detail", help="Event detail")
    event_detail.add_argument("event_id")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    token = os.environ.get("SENTRY_AUTH_TOKEN")
    if not token:
        raise RuntimeError("Missing SENTRY_AUTH_TOKEN env var.")

    base_url = args.base_url

    if args.command == "list-issues":
        data = handle_list_issues(args, token, base_url)
    elif args.command == "issue-detail":
        data = handle_issue_detail(args, token, base_url)
    elif args.command == "issue-events":
        data = handle_issue_events(args, token, base_url)
    elif args.command == "event-detail":
        data = handle_event_detail(args, token, base_url)
    else:
        raise RuntimeError(f"Unknown command: {args.command}")

    data = redact_data(data)

    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"Error: {type(exc).__name__}", file=sys.stderr)
        sys.exit(1)
