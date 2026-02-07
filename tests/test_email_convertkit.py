# tests/test_email_convertkit.py
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from leadgen.email.convertkit import ConvertKitClient


@pytest.fixture
def client():
    return ConvertKitClient(
        api_key="test-key",
        api_secret="test-secret",
    )


@pytest.mark.asyncio
async def test_add_subscriber(client):
    mock_response = {
        "subscription": {
            "id": 1,
            "subscriber": {"id": 100, "email_address": "test@example.com"},
        }
    }

    with patch("leadgen.email.convertkit.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_resp

        result = await client.add_subscriber_to_form(
            form_id="form123",
            email="test@example.com",
            first_name="Test",
        )

    assert result["subscription"]["subscriber"]["email_address"] == "test@example.com"


@pytest.mark.asyncio
async def test_list_subscribers(client):
    mock_response = {
        "total_subscribers": 42,
        "subscribers": [
            {"id": 1, "email_address": "a@example.com"},
            {"id": 2, "email_address": "b@example.com"},
        ],
    }

    with patch("leadgen.email.convertkit.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_resp

        result = await client.list_subscribers()

    assert result["total_subscribers"] == 42
    assert len(result["subscribers"]) == 2
