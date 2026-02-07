# tests/test_distributor_postiz.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.distributors.postiz import PostizDistributor


@pytest.fixture
def distributor():
    return PostizDistributor(api_key="test-api-key")


@pytest.mark.asyncio
async def test_get_integrations(distributor):
    mock_integrations = [
        {"id": "int1", "providerIdentifier": "linkedin", "name": "My Company"},
        {"id": "int2", "providerIdentifier": "x", "name": "@myhandle"},
        {"id": "int3", "providerIdentifier": "facebook", "name": "My Page"},
    ]

    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value.json.return_value = mock_integrations
        mock_client.get.return_value.raise_for_status = lambda: None

        integrations = await distributor.get_integrations()

    assert len(integrations) == 3
    assert integrations[0]["providerIdentifier"] == "linkedin"


@pytest.mark.asyncio
async def test_schedule_multi_platform_post(distributor):
    mock_response = [
        {"postId": "post1", "integration": "int1"},
        {"postId": "post2", "integration": "int2"},
    ]

    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await distributor.schedule_post(
            posts=[
                {
                    "integration_id": "int1",
                    "platform": "linkedin",
                    "content": "Check out our new blog post about AI for restaurants!",
                },
                {
                    "integration_id": "int2",
                    "platform": "x",
                    "content": "AI agents are saving restaurants 30% on costs.",
                },
            ],
            schedule_date="2026-02-10T10:00:00.000Z",
        )

    assert len(result) == 2
    assert result[0]["postId"] == "post1"


@pytest.mark.asyncio
async def test_post_now(distributor):
    mock_response = [{"postId": "post1", "integration": "int1"}]

    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await distributor.post_now(
            integration_id="int1",
            platform="facebook",
            content="New article: How AI agents help dental offices save time!",
        )

    assert result[0]["postId"] == "post1"


@pytest.mark.asyncio
async def test_check_connection(distributor):
    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value.status_code = 200
        mock_client.get.return_value.raise_for_status = lambda: None

        connected = await distributor.check_connection()

    assert connected is True
