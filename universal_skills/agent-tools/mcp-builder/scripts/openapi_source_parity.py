"""Independent raw-source route checks, without invoking the schema compiler."""

from __future__ import annotations

from operator import itemgetter
from urllib.parse import parse_qsl, quote


def source_object(document, value):
    seen = set()
    while "$ref" in value:
        ref = value["$ref"]
        if not ref.startswith("#/") or ref in seen:
            raise ValueError("Invalid source object reference")
        seen.add(ref)
        value = document
        for name in ref.removeprefix("#/").split("/"):
            value = value[name.replace("~1", "/").replace("~0", "~")]
    return value


def source_route(document, path, operation):
    parameters = {}
    shared = document["paths"][path].get("parameters", [])
    for raw in shared + operation.get("parameters", []):
        value = source_object(document, raw)
        parameters[(value["in"], value["name"])] = value
    prefix = document.get("servers", [{"url": ""}])[0].get("url", "").rstrip("/")
    body = source_object(document, operation.get("requestBody", {}))
    return {
        "path": prefix + path,
        "parameters": list(parameters.values()),
        "request_media_types": sorted(body.get("content", {})),
    }


def verify_source_routes(inventory, contract):
    for action, source in inventory["operations"].items():
        if action not in contract["operations"]:
            raise ValueError(f"Contract omitted raw source operation: {action}")
        compiled = contract["operations"][action]
        for key in ("method", "path", "parameters"):
            if compiled[key] != source[key]:
                raise ValueError(
                    f"Compiled {key} differs from independent source: {action}"
                )
        media = source["request_media_types"]
        if len(media) > 1 or compiled["content_type"] != next(iter(media), None):
            raise ValueError(f"Incomplete source request representations: {action}")


def _scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    raise ValueError("Source parameter needs an explicit serialization adapter")


def _query_values(parameter, value):
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    rendered = [_scalar(item) for item in values]
    if isinstance(value, list) and not parameter.get("explode", True):
        rendered = [",".join(rendered)]
    return [(parameter["name"], item) for item in rendered]


def verify_source_request(request, source, arguments):
    """Compare captured transport to the raw source, independent of fixtures."""
    if request.method != source["method"]:
        raise ValueError("Captured method differs from raw source")
    path, query = source["path"], []
    for parameter in source["parameters"]:
        location, name = parameter["in"], parameter["name"]
        values = arguments.get(location, {})
        if name not in values:
            continue
        value = values[name]
        if location == "path":
            path = path.replace("{" + name + "}", quote(_scalar(value), safe=""))
        elif location == "query":
            query.extend(_query_values(parameter, value))
        elif location == "header" and request.headers.get(name) != _scalar(value):
            raise ValueError("Captured header placement differs from raw source")
    _verify_route(request, path, query)


def _verify_route(request, path, query):
    actual_path = request.url.raw_path.partition(b"?")[0].decode("ascii")
    actual_query = parse_qsl(request.url.query.decode(), keep_blank_values=True)
    # Normalize key ordering only; repeated values retain array element order.
    by_key = itemgetter(0)
    if actual_path != path or sorted(actual_query, key=by_key) != sorted(
        query, key=by_key
    ):
        raise ValueError("Captured path/query placement differs from raw source")
