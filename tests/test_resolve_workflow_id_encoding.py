from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from promptlayer.utils import _resolve_workflow_id


def _make_mock_client():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"workflow": {"id": 123}}
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    return mock_client


class TestResolveWorkflowIdEncoding:
    """Tests for URL encoding of workflow names in _resolve_workflow_id."""

    @pytest.mark.asyncio
    async def test_workflow_name_with_slash_is_url_encoded(self):
        """Workflow names with slashes should be URL-encoded (%2F)."""
        workflow_name = "feature1/my_workflow"
        expected_encoded = "feature1%2Fmy_workflow"
        mock_client = _make_mock_client()

        with patch("promptlayer.utils._make_httpx_client") as mock_client_factory:
            mock_client_factory.return_value = mock_client

            result = await _resolve_workflow_id(
                "https://api.promptlayer.com", workflow_name, {"X-API-KEY": "test"}
            )

            assert result == 123
            actual_url = mock_client.get.call_args[0][0]
            assert expected_encoded in actual_url, f"Expected {expected_encoded} in URL, got {actual_url}"
            assert "/" + workflow_name not in actual_url, "Unencoded slash found in URL"

    @pytest.mark.asyncio
    async def test_workflow_name_with_spaces_is_url_encoded(self):
        """Workflow names with spaces should be URL-encoded (%20)."""
        workflow_name = "my workflow"
        expected_encoded = "my%20workflow"
        mock_client = _make_mock_client()

        with patch("promptlayer.utils._make_httpx_client") as mock_client_factory:
            mock_client_factory.return_value = mock_client

            result = await _resolve_workflow_id(
                "https://api.promptlayer.com", workflow_name, {"X-API-KEY": "test"}
            )

            assert result == 123
            actual_url = mock_client.get.call_args[0][0]
            assert expected_encoded in actual_url, f"Expected {expected_encoded} in URL, got {actual_url}"

    @pytest.mark.asyncio
    async def test_workflow_int_id_returned_as_is_without_http_call(self):
        """Integer workflow IDs should be returned as-is without any HTTP call."""
        with patch("promptlayer.utils._make_httpx_client") as mock_client_factory:
            result = await _resolve_workflow_id(
                "https://api.promptlayer.com", 456, {"X-API-KEY": "test"}
            )

            assert result == 456
            mock_client_factory.assert_not_called()
