"""Keyword research via DataForSEO API ($6/mo for 10K searches)."""

import httpx


DATAFORSEO_API = "https://api.dataforseo.com/v3"


class KeywordResearcher:
    """Research keywords for content planning."""

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def _auth(self) -> tuple[str, str]:
        return (self.login, self.password)

    async def get_suggestions(self, seed_keyword: str) -> list[dict]:
        payload = [
            {
                "keyword": seed_keyword,
                "location_code": 2840,  # United States
                "language_code": "en",
            }
        ]

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{DATAFORSEO_API}/dataforseo_labs/google/keyword_suggestions/live",
                json=payload,
                auth=self._auth(),
            )
            resp.raise_for_status()
            data = await resp.json()

        items = data["tasks"][0]["result"][0]["items"]
        return [
            {
                "keyword": item["keyword"],
                "search_volume": item["search_volume"],
                "keyword_difficulty": item["keyword_difficulty"],
            }
            for item in items
        ]

    def filter_low_competition(
        self, keywords: list[dict], max_difficulty: int = 50
    ) -> list[dict]:
        return [k for k in keywords if k["keyword_difficulty"] <= max_difficulty]
