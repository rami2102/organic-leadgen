"""Orchestrate the full content generation and distribution pipeline."""

from leadgen.content_generator import ContentGenerator
from leadgen.publishers.hugo import HugoPublisher


class LeadgenPipeline:
    """End-to-end pipeline: generate -> publish -> distribute."""

    def __init__(self, ollama_url: str, ollama_model: str, hugo_blog_dir: str):
        self.generator = ContentGenerator(base_url=ollama_url, model=ollama_model)
        self.hugo_publisher = HugoPublisher(blog_dir=hugo_blog_dir)

    async def generate_and_publish(self, niche: str, topic: str) -> dict:
        post_data = await self.generator.generate_blog_post(
            niche=niche, topic=topic
        )

        local_path = self.hugo_publisher.publish(post_data)

        return {
            "title": post_data["title"],
            "slug": post_data["slug"],
            "tags": post_data.get("tags", []),
            "local_path": local_path,
        }
