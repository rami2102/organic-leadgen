from unittest.mock import patch, AsyncMock
import pytest
from leadgen.pipeline import LeadgenPipeline


@pytest.fixture
def pipeline():
    return LeadgenPipeline(
        ollama_url="http://localhost:11434",
        ollama_model="llama3.2",
        hugo_blog_dir="/tmp/test-blog",
    )


@pytest.mark.asyncio
async def test_generate_and_publish_post(pipeline):
    mock_post = {
        "title": "Test Post",
        "slug": "test-post",
        "meta_description": "Test description",
        "body": "# Test\n\nContent",
        "tags": ["test"],
    }

    with patch.object(
        pipeline.generator, "generate_blog_post", new_callable=AsyncMock
    ) as mock_gen:
        mock_gen.return_value = mock_post

        with patch.object(
            pipeline.hugo_publisher, "publish"
        ) as mock_publish:
            from pathlib import Path
            mock_publish.return_value = Path("/tmp/test-blog/content/posts/test-post.md")

            result = await pipeline.generate_and_publish(
                niche="restaurants",
                topic="AI chatbots for reservations",
            )

    assert result["title"] == "Test Post"
    assert result["local_path"].name == "test-post.md"
    mock_gen.assert_called_once()
    mock_publish.assert_called_once()
