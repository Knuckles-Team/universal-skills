"""Bound response bytes and decode only declared success representations."""

import base64
import json
import time


def read_body(response, max_bytes, *, deadline):
    body = bytearray()
    for chunk in response.iter_bytes():
        if time.monotonic() > deadline or len(body) + len(chunk) > max_bytes:
            raise RuntimeError("Provider response limit exceeded")
        body.extend(chunk)
    return body


def _decode_json(body):
    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Provider response is not JSON") from exc


def _decode_text(body, encoding):
    try:
        return body.decode(encoding or "utf-8")
    except (UnicodeDecodeError, LookupError) as exc:
        raise ValueError("Provider text response cannot be decoded") from exc


def decode_body(operation, response, body):
    status = str(response.status_code)
    expected = operation["responses"].get(status)
    if expected is None:
        raise ValueError("Undeclared provider success status")
    if not expected:
        if body:
            raise ValueError("Unexpected provider response body")
        return "", None
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip()
    if content_type not in expected:
        raise ValueError("Undeclared provider response media type")
    mode = operation["response_modes"][status][content_type]
    decoders = {
        "json": lambda: _decode_json(body),
        "text": lambda: _decode_text(body, response.charset_encoding),
    }
    data = decoders.get(mode, lambda: base64.b64encode(body).decode())()
    return content_type, data
