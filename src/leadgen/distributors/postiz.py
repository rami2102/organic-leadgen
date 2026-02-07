"""Schedule social posts via Postiz API (27+ platforms, multi-platform per request).

API docs: https://docs.postiz.com/public-api
Rate limit: 30 requests/hour (counts API calls, not posts).
Auth: Raw API key in Authorization header (no Bearer prefix).
"""

from datetime import datetime, timezone

import httpx


DEFAULT_BASE_URL = "https://api.postiz.com/public/v1"

# Platform-specific settings templates
PLATFORM_SETTINGS = {
    "x": {"__type": "x", "who_can_reply_post": "everyone"},
    "linkedin": {"__type": "linkedin"},
    "facebook": {"__type": "facebook"},
    "instagram": {"__type": "instagram", "post_type": "post"},
    "threads": {"__type": "threads"},
    "bluesky": {"__type": "bluesky"},
    "tiktok": {"__type": "tiktok"},
    "youtube": {"__type": "youtube", "type": "public"},
    "reddit": {"__type": "reddit"},
    "mastodon": {"__type": "mastodon"},
}


class PostizDistributor:
    """Distribute social posts through Postiz (27+ platforms)."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict:
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    async def check_connection(self) -> bool:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/check-connection",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.status_code == 200

    async def get_integrations(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/integrations",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return await resp.json()

    async def schedule_post(
        self,
        posts: list[dict],
        schedule_date: str,
    ) -> list[dict]:
        """Schedule posts to multiple platforms in a single API call.

        Args:
            posts: List of dicts with keys: integration_id, platform, content, image (optional)
            schedule_date: ISO 8601 UTC timestamp (e.g. "2026-02-10T10:00:00.000Z")
        """
        payload = {
            "type": "schedule",
            "date": schedule_date,
            "shortLink": False,
            "tags": [],
            "posts": [
                {
                    "integration": {"id": p["integration_id"]},
                    "value": [
                        {
                            "content": p["content"],
                            "image": p.get("image", []),
                        }
                    ],
                    "settings": PLATFORM_SETTINGS.get(
                        p["platform"], {"__type": p["platform"]}
                    ),
                }
                for p in posts
            ],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/posts",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return await resp.json()

    async def post_now(
        self,
        integration_id: str,
        platform: str,
        content: str,
        image: list | None = None,
    ) -> list[dict]:
        """Publish a post immediately to a single platform."""
        payload = {
            "type": "now",
            "date": datetime.now(timezone.utc).isoformat(),
            "shortLink": False,
            "tags": [],
            "posts": [
                {
                    "integration": {"id": integration_id},
                    "value": [
                        {
                            "content": content,
                            "image": image or [],
                        }
                    ],
                    "settings": PLATFORM_SETTINGS.get(
                        platform, {"__type": platform}
                    ),
                }
            ],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/posts",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return await resp.json()
