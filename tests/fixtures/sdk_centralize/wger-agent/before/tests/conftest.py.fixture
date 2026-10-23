import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_requests_session():
    with patch("requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # Default mock response for the initialization check on /workout/
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_session.get.return_value = mock_response
        mock_session.post.return_value = mock_response
        mock_session.patch.return_value = mock_response
        mock_session.put.return_value = mock_response

        # delete should return a response with raise_for_status
        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 204
        mock_session.delete.return_value = mock_delete_response

        yield mock_session


@pytest.fixture(autouse=True)
def mock_sys_argv():
    with patch("sys.argv", ["mcp-server"]):
        yield
