from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from leadgen.publishers.devto import DevtoPublisher


@pytest.fixture
def publisher():
    return DevtoPublisher(api_key="test-key")


@pytest.mark.asyncio
async def test_devto_publish(publisher):
    mock_response = {
        "id": 12345,
        "url": "https://dev.to/username/test-post-abc",
    }

    with patch("leadgen.publishers.devto.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_resp
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await publisher.publish({
            "title": "Test Post",
            "body": "Content here",
            "tags": ["ai", "automation"],
            "canonical_url": "https://yourdomain.com/posts/test-post/",
        })

    assert result["id"] == 12345
    assert "url" in result
