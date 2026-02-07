"""Cross-post articles to Dev.to via REST API."""

import httpx


DEVTO_API = "https://dev.to/api/articles"


class DevtoPublisher:
    """Publish articles to Dev.to."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def publish(self, post_data: dict) -> dict:
        payload = {
            "article": {
                "title": post_data["title"],
                "body_markdown": post_data["body"],
                "published": True,
                "tags": post_data.get("tags", [])[:4],
                "canonical_url": post_data.get("canonical_url", ""),
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                DEVTO_API,
                json=payload,
                headers={"api-key": self.api_key},
            )
            resp.raise_for_status()
            data = resp.json()

        return {"id": data["id"], "url": data["url"]}
