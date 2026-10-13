"""Serialize only parameters and body types declared by an OpenAPI operation."""

import base64
import json
from urllib.parse import quote


def _value(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (str, int, float)):
        return str(value)
    raise ValueError("Unsupported parameter value")


def _path_parameter(path, name, value):
    rendered = _value(value)
    if rendered in {".", ".."} or any(c in rendered for c in "/\\%\r\n\x00"):
        raise ValueError("Unsafe path parameter")
    return path.replace("{" + name + "}", quote(rendered, safe=""))


def _query_parameter(parameter, value):
    name = parameter["name"]
    if value is None:
        return []
    if not isinstance(value, list):
        return [(name, _value(value))]
    rendered = [_value(item) for item in value]
    if parameter.get("explode", True):
        return [(name, item) for item in rendered]
    return [(name, ",".join(rendered))]


def _header_parameter(name, value, credential_headers):
    if name.casefold() in credential_headers:
        raise ValueError("Authentication headers are controlled by credentials")
    rendered = _value(value)
    if any(c in rendered for c in "\r\n\x00"):
        raise ValueError("Invalid header parameter")
    return rendered


def parameters(operation, arguments, *, credential_headers):
    path, query, headers = operation["path"], [], {}
    for parameter in operation["parameters"]:
        name, location = parameter["name"], parameter["in"]
        values = arguments.get(location, {})
        if name not in values:
            continue
        value = values[name]
        if location == "path":
            path = _path_parameter(path, name, value)
        elif location == "query":
            query.extend(_query_parameter(parameter, value))
        elif location == "header":
            headers[name] = _header_parameter(name, value, credential_headers)
    if "{" in path or "}" in path:
        raise ValueError("Missing path parameter")
    return path, query, headers


def _multipart(body, body_schema, *, definitions, max_bytes):
    while "$ref" in body_schema:
        body_schema = definitions[body_schema["$ref"].rsplit("/", 1)[1]]
    files, data = {}, {}
    for key, value in body.items():
        field = body_schema.get("properties", {}).get(key, {})
        if field.get("contentEncoding") == "base64":
            decoded = _decode_upload(value, max_bytes)
            files[key] = ("upload", decoded, "application/octet-stream")
        else:
            data[key] = (
                json.dumps(value, separators=(",", ":"))
                if isinstance(value, (dict, list))
                else _value(value)
            )
    return _multipart_options(files, data)


def _multipart_options(files, data):
    # HTTPX selects form encoding when files is empty. Optional file fields
    # must not silently change the operation's declared multipart media type.
    if files:
        return {"files": files, "data": data}
    if data:
        return {"files": {key: (None, value) for key, value in data.items()}}
    return {
        "content": b"--mcp-empty-body--\r\n",
        "headers": {"Content-Type": "multipart/form-data; boundary=mcp-empty-body"},
    }


def body_options(operation, body, *, definitions, max_bytes):
    if len(json.dumps(body).encode()) > max_bytes:
        raise ValueError("Request size limit exceeded")
    media = operation["content_type"]
    if media == "application/json":
        return {"json": body}
    if media == "application/x-www-form-urlencoded":
        return {"data": body}
    if media == "multipart/form-data":
        return _multipart(
            body,
            operation["input"]["properties"]["body"],
            definitions=definitions,
            max_bytes=max_bytes,
        )
    raise ValueError("Unsupported operation request media type")


def _decode_upload(value, max_bytes):
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid base64 upload") from exc
    if len(decoded) > max_bytes:
        raise ValueError("Upload size limit exceeded")
    return decoded
