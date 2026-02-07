# tests/test_seo_keywords.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.seo.keywords import KeywordResearcher


@pytest.fixture
def researcher():
    return KeywordResearcher(
        login="test-login",
        password="test-password",
    )


@pytest.mark.asyncio
async def test_get_keyword_suggestions(researcher):
    mock_response = {
        "tasks": [
            {
                "result": [
                    {
                        "items": [
                            {
                                "keyword": "ai chatbot for restaurants",
                                "search_volume": 1200,
                                "keyword_difficulty": 35,
                            },
                            {
                                "keyword": "restaurant automation software",
                                "search_volume": 800,
                                "keyword_difficulty": 42,
                            },
                        ]
                    }
                ]
            }
        ]
    }

    with patch("leadgen.seo.keywords.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        results = await researcher.get_suggestions("ai agents for restaurants")

    assert len(results) == 2
    assert results[0]["keyword"] == "ai chatbot for restaurants"
    assert results[0]["search_volume"] == 1200


def test_filter_low_competition(researcher):
    keywords = [
        {"keyword": "easy", "keyword_difficulty": 20, "search_volume": 500},
        {"keyword": "hard", "keyword_difficulty": 80, "search_volume": 5000},
        {"keyword": "medium", "keyword_difficulty": 45, "search_volume": 1000},
    ]
    filtered = researcher.filter_low_competition(keywords, max_difficulty=50)
    assert len(filtered) == 2
    assert all(k["keyword_difficulty"] <= 50 for k in filtered)
