from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from leadgen.publishers.hashnode import HashnodePublisher


@pytest.fixture
def publisher():
    return HashnodePublisher(
        api_token="test-token",
        publication_id="test-pub-id",
    )


@pytest.mark.asyncio
async def test_hashnode_publish(publisher):
    mock_response = {
        "data": {
            "publishPost": {
                "post": {
                    "id": "abc123",
                    "url": "https://blog.example.com/test-post",
                }
            }
        }
    }

    with patch("leadgen.publishers.hashnode.httpx.AsyncClient") as MockClient:
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
            "slug": "test-post",
            "canonical_url": "https://yourdomain.com/posts/test-post/",
        })

    assert result["id"] == "abc123"
    assert "url" in result
