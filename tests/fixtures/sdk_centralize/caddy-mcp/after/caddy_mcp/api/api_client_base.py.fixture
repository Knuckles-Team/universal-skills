from typing import Any
from urllib.parse import urljoin

import httpx
from scion_sdk.auth.static import BearerAuth
from scion_sdk.http.client import create_http_client
from scion_sdk.http.options import HttpClientOptions
from scion_sdk.tls.profile import ResolvedTLSProfile
from scion_sdk.tls.resolve import resolve_tls_profile


class ApiClientBase:
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        self.base_url = base_url
        self.token = token
        self.username = username
        self.password = password
        self.last_etag: str | None = None
        auth: httpx.Auth | None = None
        self.tls_profile = tls_profile or resolve_tls_profile("caddy")

        if token:
            auth = BearerAuth(token)
        elif username and password:
            auth = httpx.BasicAuth(username, password)
        self._session = create_http_client(
            HttpClientOptions(
                base_url=self.base_url,
                tls=self.tls_profile,
                auth=auth,
                allow_plaintext=self.base_url.startswith("http://"),
            )
        )

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = urljoin(self.base_url, endpoint)

        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        content_type = req_headers.get("Content-Type", "")
        kwargs: dict[str, Any] = {}

        if "application/json" in content_type:
            if isinstance(data, str):
                kwargs["data"] = data
            else:
                kwargs["json"] = data
        else:
            kwargs["data"] = data

        response = self._session.request(
            method=method,
            url=url,
            headers=req_headers,
            params=params,
            **kwargs,
        )

        self.last_etag = response.headers.get("ETag")

        if response.status_code >= 400:
            raise Exception(f"API error: {response.status_code}")

        if response.status_code == 204 or not response.text.strip():
            return {"status": "success"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "text": response.text}
