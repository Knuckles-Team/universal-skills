"""Bound response bytes and decode only declared success representations."""

import base64
import json
import time

from rfc3986_validator import validate_rfc3986


def require_response_status(operation, status):
    if 200 <= status < 300 or str(status) in operation.get("redirect_responses", {}):
        return
    raise RuntimeError(f"Provider returned HTTP {status}; no automatic retry")


def _redirect_data(response):
    values = response.headers.get_list("location")
    if len(values) != 1:
        raise ValueError("Redirect requires exactly one Location header")
    location = values[0]
    if not location.isprintable() or not validate_rfc3986(location, rule="URI"):
        raise ValueError(
            "Redirect Location must be an absolute URI without unsafe characters"
        )
    return "", {"location": location}


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
    if status in operation.get("redirect_responses", {}):
        return _redirect_data(response)
    return _declared_body(operation, response, body)


def _declared_body(operation, response, body):
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
