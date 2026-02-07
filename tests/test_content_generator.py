# tests/test_content_generator.py
import json
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.content_generator import ContentGenerator


@pytest.fixture
def generator():
    return ContentGenerator(model="sonnet")


def test_generator_init(generator):
    assert generator.model == "sonnet"


@pytest.mark.asyncio
async def test_generate_blog_post(generator):
    mock_response = {
        "title": "5 Ways AI Agents Save Restaurants Money",
        "slug": "5-ways-ai-agents-save-restaurants-money",
        "meta_description": "Discover how AI agents help restaurants cut costs.",
        "body": "# 5 Ways AI Agents Save Restaurants Money\n\nContent here...",
        "tags": ["ai", "restaurants", "automation"],
    }

    with patch.object(
        generator, "_call_claude", new_callable=AsyncMock
    ) as mock_call:
        mock_call.return_value = mock_response
        result = await generator.generate_blog_post(
            niche="restaurants",
            topic="cost savings from AI agents",
        )

    assert result["title"] == "5 Ways AI Agents Save Restaurants Money"
    assert result["slug"] == "5-ways-ai-agents-save-restaurants-money"
    assert "body" in result
    assert "tags" in result


@pytest.mark.asyncio
async def test_generate_social_posts(generator):
    mock_response = {
        "linkedin": "Restaurants using AI agents report 30% cost savings...",
        "x": "AI agents are saving restaurants 30% on labor costs. Here's how:",
        "facebook": "Did you know? Restaurants using AI agents save an average of 30%...",
        "instagram": "The future of restaurants is here. AI agents are saving 30%...",
        "threads": "Hot take: restaurants not using AI agents in 2026 are leaving money on the table.",
    }

    with patch.object(
        generator, "_call_claude", new_callable=AsyncMock
    ) as mock_call:
        mock_call.return_value = mock_response
        result = await generator.repurpose_to_social(
            blog_title="5 Ways AI Agents Save Restaurants Money",
            blog_body="Full blog content here...",
        )

    assert "linkedin" in result
    assert "x" in result
    assert "instagram" in result
    assert len(result["x"]) <= 280
