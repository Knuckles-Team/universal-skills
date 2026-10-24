"""Provider client with operation-bound OpenAPI dispatch."""

from ..openapi_runtime import OpenApiClientBase


class ApiClientSystem(OpenApiClientBase):
    """Use the canonical client factory with validated domain actions."""
