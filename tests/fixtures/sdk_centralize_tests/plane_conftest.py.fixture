from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_session():
    """Shared requests.Session mock fixture for Plane API tests."""
    with patch("requests.Session") as mock_s:
        session = mock_s.return_value
        session.status_code = 200
        session.response_json = {
            "status": "success",
            "results": [{"id": "mock_id", "name": "mock_name"}],
            "id": "mock_id",
            "name": "mock_name",
            "features": {},
        }

        def mock_request(method, url, *args, **kwargs):
            response = MagicMock()
            response.status_code = getattr(session, "status_code", 200)

            # Allow raising standard raise_for_status
            if response.status_code >= 400:
                import requests

                err = requests.HTTPError(response=response)
                response.raise_for_status.side_effect = err
            else:
                response.raise_for_status.side_effect = lambda: None

            if getattr(session, "response_json", None) is not None:
                response.json.return_value = session.response_json
            else:
                response.json.return_value = {}

            return response

        session.get.side_effect = lambda url, *a, **k: mock_request("GET", url, *a, **k)
        session.post.side_effect = lambda url, *a, **k: mock_request(
            "POST", url, *a, **k
        )
        session.patch.side_effect = lambda url, *a, **k: mock_request(
            "PATCH", url, *a, **k
        )
        session.delete.side_effect = lambda url, *a, **k: mock_request(
            "DELETE", url, *a, **k
        )
        yield session
