#!/usr/bin/env python3
"""
Google Chat API operations.
Lightweight alternative to the full Google Workspace MCP server.
"""

import argparse
import json
import mimetypes
import os
import re
import secrets
import sys
import urllib.parse
from typing import Optional
from urllib.request import Request

from auth import get_valid_access_token
from universal_skills._security.http import (
    SafeHttpError,
    SafeHttpStatus,
    UrlPolicy,
    open_json,
)

CHAT_API_BASE = "https://chat.googleapis.com/v1"
CHAT_UPLOAD_BASE = "https://chat.googleapis.com/upload/v1"
SPACE_NAME_RE = re.compile(r"^spaces/[A-Za-z0-9_-]{1,256}$")


def api_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
) -> dict:
    """Make an authenticated request to the Google Chat API."""
    token = get_valid_access_token()
    if not token:
        return {"error": "Failed to get access token"}

    url = f"{CHAT_API_BASE}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    body = json.dumps(data).encode("utf-8") if data else None

    try:
        req = Request(url, data=body, headers=headers, method=method)
        payload, _ = open_json(
            req,
            policy=UrlPolicy(frozenset({"chat.googleapis.com"})),
            timeout=30,
            max_bytes=8 * 1024 * 1024,
        )
        return payload if isinstance(payload, dict) else {"success": True}
    except SafeHttpStatus as e:
        return {"error": f"Remote service returned HTTP {e.status}"}
    except SafeHttpError:
        return {"error": "Remote service request failed"}


def upload_attachment(space_name: str, file_path: str, text: str = "") -> dict:
    """Send a message with a file attachment (two-step: upload then send)."""

    token = get_valid_access_token()
    if not token:
        return {"error": "Failed to get access token"}

    if SPACE_NAME_RE.fullmatch(space_name) is None:
        return {"error": "Invalid space identifier"}
    if not os.path.isfile(file_path) or os.path.islink(file_path):
        return {"error": "Configured file was not found"}
    if os.path.getsize(file_path) > 32 * 1024 * 1024:
        return {"error": "Configured file exceeds the upload boundary"}

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    filename = os.path.basename(file_path)
    # Step 1: Upload the file to get an attachment token
    upload_url = f"{CHAT_UPLOAD_BASE}/{space_name}/attachments:upload"
    metadata = json.dumps({"filename": filename})
    boundary = "skill-" + secrets.token_hex(16)
    try:
        with open(file_path, "rb") as stream:
            file_content = stream.read(32 * 1024 * 1024 + 1)
        if len(file_content) > 32 * 1024 * 1024:
            return {"error": "Configured file exceeds the upload boundary"}
        multipart = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{metadata}\r\n--{boundary}\r\nContent-Type: {mime_type}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"upload\"\r\n\r\n"
        ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()
        request = Request(
            upload_url + "?uploadType=multipart",
            data=multipart,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/related; boundary={boundary}",
            },
            method="POST",
        )
        upload_data, _ = open_json(
            request,
            policy=UrlPolicy(frozenset({"chat.googleapis.com"})),
            timeout=60,
            max_bytes=8 * 1024 * 1024,
        )
    except SafeHttpStatus as error:
        return {"error": f"Remote service returned HTTP {error.status}"}
    except (OSError, SafeHttpError):
        return {"error": "Remote service request failed"}
    if not isinstance(upload_data, dict):
        return {"error": "Invalid upload response"}
    attachment_token = upload_data.get("attachmentDataRef", {}).get(
        "attachmentUploadToken"
    )
    if not attachment_token:
        return {"error": "Upload succeeded but no attachment token returned"}

    # Step 2: Send message with the attachment reference
    msg_data = {
        "text": text,
        "attachment": [
            {
                "contentName": filename,
                "contentType": mime_type,
                "attachmentDataRef": {"attachmentUploadToken": attachment_token},
            }
        ],
    }

    return api_request("POST", f"{space_name}/messages", data=msg_data)


def list_spaces() -> dict:
    """List all spaces the user is a member of."""
    result = api_request("GET", "spaces")
    return result.get("spaces", []) if "spaces" in result else result


def find_space_by_name(display_name: str) -> dict:
    """Find a space by its display name."""
    spaces = list_spaces()
    if isinstance(spaces, dict) and "error" in spaces:
        return spaces

    matching = [s for s in spaces if s.get("displayName") == display_name]
    if matching:
        return {"spaces": matching}
    return {"error": f"No space found with display name: {display_name}"}


def get_messages(
    space_name: str,
    page_size: int = 25,
    page_token: Optional[str] = None,
    order_by: str = "createTime desc",
) -> dict:
    """Get messages from a space."""
    params = {"pageSize": page_size, "orderBy": order_by}
    if page_token:
        params["pageToken"] = page_token

    return api_request("GET", f"{space_name}/messages", params=params)


def send_message(space_name: str, text: str, attachment: Optional[str] = None) -> dict:
    """Send a message to a space, optionally with a file attachment."""
    if attachment:
        return upload_attachment(space_name, attachment, text)
    return api_request("POST", f"{space_name}/messages", data={"text": text})


def send_dm(email: str, text: str, attachment: Optional[str] = None) -> dict:
    """Send a direct message to a user by email, optionally with a file attachment."""
    # First, set up or find the DM space
    space_data = {
        "space": {"spaceType": "DIRECT_MESSAGE"},
        "memberships": [{"member": {"name": f"users/{email}", "type": "HUMAN"}}],
    }
    space_result = api_request("POST", "spaces:setup", data=space_data)

    if "error" in space_result:
        return space_result

    space_name = space_result.get("name")
    if not space_name:
        return {"error": "Failed to create DM space"}

    # Send the message (with or without attachment)
    if attachment:
        return upload_attachment(space_name, attachment, text)
    return api_request("POST", f"{space_name}/messages", data={"text": text})


def find_dm_by_email(email: str) -> dict:
    """Find or create a DM space with a user."""
    space_data = {
        "space": {"spaceType": "DIRECT_MESSAGE"},
        "memberships": [{"member": {"name": f"users/{email}", "type": "HUMAN"}}],
    }
    return api_request("POST", "spaces:setup", data=space_data)


def list_threads(
    space_name: str, page_size: int = 25, page_token: Optional[str] = None
) -> dict:
    """List threads from a space."""
    params = {"pageSize": page_size, "orderBy": "createTime desc"}
    if page_token:
        params["pageToken"] = page_token

    result = api_request("GET", f"{space_name}/messages", params=params)

    if "error" in result:
        return result

    # Group messages by thread
    messages = result.get("messages", [])
    seen_threads = set()
    threads = []

    for msg in messages:
        thread_name = msg.get("thread", {}).get("name")
        if thread_name and thread_name not in seen_threads:
            threads.append(msg)
            seen_threads.add(thread_name)

    return {"threads": threads, "nextPageToken": result.get("nextPageToken")}


def setup_space(display_name: str, user_emails: list) -> dict:
    """Create a new space with members."""
    memberships = [
        {"member": {"name": f"users/{email}", "type": "HUMAN"}} for email in user_emails
    ]
    space_data = {
        "space": {"spaceType": "SPACE", "displayName": display_name},
        "memberships": memberships,
    }
    return api_request("POST", "spaces:setup", data=space_data)


def main():
    parser = argparse.ArgumentParser(description="Google Chat API operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-spaces
    subparsers.add_parser("list-spaces", help="List all spaces")

    # find-space
    find_space_parser = subparsers.add_parser(
        "find-space", help="Find a space by display name"
    )
    find_space_parser.add_argument("name", help="Display name of the space")

    # get-messages
    get_messages_parser = subparsers.add_parser(
        "get-messages", help="Get messages from a space"
    )
    get_messages_parser.add_argument("space", help="Space name (e.g., spaces/AAAA123)")
    get_messages_parser.add_argument(
        "--limit", type=int, default=25, help="Max messages to return"
    )
    get_messages_parser.add_argument("--page-token", help="Pagination token")

    # send-message
    send_message_parser = subparsers.add_parser(
        "send-message", help="Send a message to a space"
    )
    send_message_parser.add_argument("space", help="Space name (e.g., spaces/AAAA123)")
    send_message_parser.add_argument("text", nargs="?", default="", help="Message text")
    send_message_parser.add_argument("--attachment", help="Path to file to attach")

    # send-dm
    send_dm_parser = subparsers.add_parser("send-dm", help="Send a direct message")
    send_dm_parser.add_argument("email", help="Recipient email address")
    send_dm_parser.add_argument("text", nargs="?", default="", help="Message text")
    send_dm_parser.add_argument("--attachment", help="Path to file to attach")

    # find-dm
    find_dm_parser = subparsers.add_parser("find-dm", help="Find or create DM space")
    find_dm_parser.add_argument("email", help="User's email address")

    # list-threads
    list_threads_parser = subparsers.add_parser(
        "list-threads", help="List threads in a space"
    )
    list_threads_parser.add_argument("space", help="Space name")
    list_threads_parser.add_argument(
        "--limit", type=int, default=25, help="Max threads to return"
    )

    # setup-space
    setup_space_parser = subparsers.add_parser("setup-space", help="Create a new space")
    setup_space_parser.add_argument("name", help="Display name for the space")
    setup_space_parser.add_argument("emails", nargs="+", help="Member email addresses")

    args = parser.parse_args()

    if args.command == "list-spaces":
        result = list_spaces()
    elif args.command == "find-space":
        result = find_space_by_name(args.name)
    elif args.command == "get-messages":
        result = get_messages(args.space, args.limit, args.page_token)
    elif args.command == "send-message":
        result = send_message(args.space, args.text, getattr(args, "attachment", None))
    elif args.command == "send-dm":
        result = send_dm(args.email, args.text, getattr(args, "attachment", None))
    elif args.command == "find-dm":
        result = find_dm_by_email(args.email)
    elif args.command == "list-threads":
        result = list_threads(args.space, args.limit)
    elif args.command == "setup-space":
        result = setup_space(args.name, args.emails)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))

    if isinstance(result, dict) and "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
