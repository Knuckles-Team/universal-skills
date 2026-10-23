#!/usr/bin/env python
import logging
from typing import Any

import requests
from agent_connector_sdk.exceptions import AuthError, UnauthorizedError
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile

logger = logging.getLogger(__name__)


class BaseApiClient:
    def __init__(
        self,
        base_url: str = "https://wger.de",
        token: str = "",  # nosec B107
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_base = f"{self.base_url}/api/v2"
        self.tls_profile = tls_profile or resolve_tls_profile("wger")
        self.session = self.tls_profile.configure_requests_session(requests.Session())
        if token:
            self.session.headers.update({"Authorization": f"Token {token}"})
        self.session.headers.update({"Accept": "application/json"})

        try:
            response = self.session.get(f"{self.api_base}/workout/")
            if response.status_code == 401:
                raise AuthError("Wger authentication failed: Invalid API key.")
            elif response.status_code == 403:
                raise UnauthorizedError(
                    "Wger access forbidden: Insufficient permissions."
                )
            response.raise_for_status()
        except Exception as e:
            if isinstance(e, (AuthError, UnauthorizedError)):
                raise e
            pass

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self.session.close()
        self.tls_profile.cleanup()

    def _url(self, endpoint: str) -> str:
        return f"{self.api_base}/{endpoint.strip('/')}/"

    def _get(self, endpoint: str, params: dict | None = None) -> Any:
        resp = self.session.get(self._url(endpoint), params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, endpoint: str, data: dict | None = None) -> Any:
        resp = self.session.post(self._url(endpoint), json=data)
        resp.raise_for_status()
        return resp.json()

    def _put(self, endpoint: str, data: dict | None = None) -> Any:
        resp = self.session.put(self._url(endpoint), json=data)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, endpoint: str, data: dict | None = None) -> Any:
        resp = self.session.patch(self._url(endpoint), json=data)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, endpoint: str) -> bool:
        resp = self.session.delete(self._url(endpoint))
        resp.raise_for_status()
        return True

    def _list(
        self,
        endpoint: str,
        limit: int | None = None,
        offset: int | None = None,
        ordering: str | None = None,
        **filters,
    ) -> dict:
        params = {k: v for k, v in filters.items() if v is not None}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if ordering:
            params["ordering"] = ordering
        return self._get(endpoint, params=params)

    def _config_crud(
        self,
        config_type: str,
        config_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs,
    ):
        """Generic CRUD for config endpoints (weight, reps, sets, rest, rir)."""
        if config_id and not kwargs:
            return self._get(f"{config_type}/{config_id}")
        elif config_id and kwargs.get("_delete"):
            return self._delete(f"{config_type}/{config_id}")
        elif config_id:
            return self._patch(f"{config_type}/{config_id}", data=kwargs)
        elif kwargs:
            return self._post(config_type, data=kwargs)
        else:
            return self._list(config_type, limit=limit, offset=offset)
