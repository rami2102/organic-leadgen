"""ConvertKit API client (free tier: 10K subscribers, unlimited emails)."""

import httpx


CONVERTKIT_API = "https://api.convertkit.com/v3"


class ConvertKitClient:
    """Manage subscribers and forms via ConvertKit."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    async def add_subscriber_to_form(
        self,
        form_id: str,
        email: str,
        first_name: str = "",
    ) -> dict:
        payload = {
            "api_key": self.api_key,
            "email": email,
        }
        if first_name:
            payload["first_name"] = first_name

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{CONVERTKIT_API}/forms/{form_id}/subscribe",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def list_subscribers(self) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CONVERTKIT_API}/subscribers",
                params={"api_secret": self.api_secret},
            )
            resp.raise_for_status()
            return resp.json()
