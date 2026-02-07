from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import pytest
from leadgen.pipeline import LeadgenPipeline


@pytest.fixture
def pipeline():
    p = LeadgenPipeline(
        ollama_url="http://localhost:11434",
        ollama_model="llama3.2",
        hugo_blog_dir="/tmp/test-blog",
    )
    return p


@pytest.mark.asyncio
async def test_full_pipeline_with_cross_post_and_social(pipeline):
    mock_post = {
        "title": "Test Post",
        "slug": "test-post",
        "meta_description": "Test",
        "body": "# Test\n\nContent",
        "tags": ["test"],
    }
    mock_social = {
        "linkedin": "LinkedIn post text...",
        "x": "X/Twitter post text...",
        "facebook": "Facebook post text...",
        "instagram": "Instagram post text...",
        "threads": "Threads post text...",
    }

    with patch.object(
        pipeline.generator, "generate_blog_post", new_callable=AsyncMock
    ) as mock_gen, patch.object(
        pipeline.generator, "repurpose_to_social", new_callable=AsyncMock
    ) as mock_social_gen, patch.object(
        pipeline.hugo_publisher, "publish"
    ) as mock_publish:

        mock_gen.return_value = mock_post
        mock_social_gen.return_value = mock_social
        mock_publish.return_value = Path("/tmp/test-blog/content/posts/test-post.md")

        result = await pipeline.generate_and_publish(
            niche="restaurants",
            topic="AI chatbots",
        )

        social = await pipeline.generator.repurpose_to_social(
            blog_title=result["title"],
            blog_body=mock_post["body"],
        )

    assert "linkedin" in social
    assert "x" in social
    assert len(social["x"]) <= 280
